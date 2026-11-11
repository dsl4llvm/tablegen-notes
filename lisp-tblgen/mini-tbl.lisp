;;;; mini-tbl.lisp —— TableGen 的"记录层"，用 Common Lisp 重写一遍。
;;;; 支持：class（单继承）、def、class 参数、字段覆盖、multiclass/defm、匿名 def、字段类型检查。
;;;; 不支持：include、foreach、!if、!cast、多继承、位域、模板特化。
;;;; 目的不是替代 tblgen，而是把"宏展开成一张记录表"这件事摊开给人看。

(defpackage :mini-tbl (:use :cl) (:export :run :dump-json :*records*))
(in-package :mini-tbl)

;;; ---------------------------------------------------------------- 数据结构

(defstruct field name type init)
(defstruct klass name params super fields)

(defvar *classes* (make-hash-table :test #'equal))
(defvar *multis*  (make-hash-table :test #'equal))
(defvar *records* '())
(defvar *anon* 0)

(defun class-fields (name)
  "继承来的在前，自己的在后。"
  (let ((k (gethash name *classes*)))
    (unless k (error "unknown class: ~a" (string name)))
    (append (when (klass-super k) (class-fields (klass-super k)))
            (klass-fields k))))

;;; ---------------------------------------------------------------- 求值

(defun eval-expr (form env)
  "只处理三种情况：模板参数、字面量、以及被参数引用的列表。"
  (cond ((and (symbolp form) (assoc form env)) (cdr (assoc form env)))
        ((consp form) (mapcar (lambda (x) (eval-expr x env)) form))
        (t form)))

;;; ---------------------------------------------------------------- 类型

(defun type-ok-p (type value)
  (let ((t* (string-upcase (symbol-name type))))
    (cond ((string= t* "INT")    (integerp value))
          ((string= t* "BIT")    (member value '(0 1)))
          ((string= t* "STRING") (stringp value))
          ((string= t* "LIST")   (listp value))
          ((string= t* "DAG")    (and (listp value) (symbolp (first value))))
          (t (error "unknown type: ~a" type)))))

(defun check-field (type value where)
  (unless (type-ok-p type value)
    (error "~a: expects ~a, got ~s" where type value))
  value)

;;; ---------------------------------------------------------------- def

(defun expand-def (spec prefix env)
  "(def Name (Class arg...) ((Field val)...))；Name 可以是 :anon。"
  (destructuring-bind (name (class-name &rest args) overrides) (rest spec)
    (let* ((klass   (or (gethash (string class-name) *classes*)
                        (error "unknown class: ~a" class-name)))
           (arg-vals (mapcar (lambda (a) (eval-expr a env)) args))
           (env2     (append (mapcar #'cons (klass-params klass) arg-vals) env))
           (fields   (mapcar (lambda (f)
                               (cons (field-name f)
                                     (check-field (field-type f)
                                                  (eval-expr (field-init f) env2)
                                                  (format nil "~a.~a" name (field-name f)))))
                             (class-fields (klass-name klass)))))
      ;; 覆盖：值同样在"class 参数"作用域里求值
      (dolist (ov overrides)
        (let* ((fname (string (first ov)))
               (cell  (assoc fname fields :test #'string-equal)))
          (unless cell (error "~a: no field ~a" name fname))
          (rplacd cell (check-field (field-type (find fname (class-fields (klass-name klass))
                                                     :key #'field-name :test #'string-equal))
                                    (eval-expr (second ov) env2)
                                    (format nil "~a.~a" name fname)))))
      (let ((real (if (and (symbolp name) (string-equal (symbol-name name) "ANON"))
                      (format nil "anonymous_~d" (1- (incf *anon*)))
                      (concatenate 'string prefix (string name)))))
        (push (list :name real :class (klass-name klass)
                    :supers (list (klass-name klass)) :fields fields)
              *records*)))))

;;; ---------------------------------------------------------------- defm

(defun expand-defm (spec env)
  "(defm Prefix (Multi arg...))：展开 multiclass 体里的每条 def。"
  (destructuring-bind (prefix (multi &rest args)) (rest spec)
    (let* ((m (gethash (string multi) *multis*))
           (_ (unless m (error "unknown multiclass: ~a" multi)))
           (env2 (append (mapcar #'cons (first m) (mapcar (lambda (a) (eval-expr a env)) args)) env)))
      (declare (ignore _))
      (dolist (d (second m))
        (expand-def d (string prefix) env2)))))

;;; ---------------------------------------------------------------- 主循环

(defun run (forms)
  (dolist (f forms)
    (let ((kind (string-upcase (symbol-name (first f)))))
      (cond
        ((string= kind "CLASS")
         (let ((k (make-klass :name (string (second f)) :params (third f)
                              :super (let ((s (first (fourth f)))) (and s (string s)))
                              :fields (mapcar (lambda (fd)
                                                (make-field :name (string (first fd))
                                                            :type (second fd)
                                                            :init (third fd)))
                                              (cddddr f)))))
           (setf (gethash (klass-name k) *classes*) k)))
        ((string= kind "MULTICLASS")
         (setf (gethash (string (second f)) *multis*) (list (third f) (cdddr f))))
        ((string= kind "DEF")  (expand-def f "" nil))
        ((string= kind "DEFM") (expand-defm f nil))
        (t (error "unknown form: ~a" (first f))))))
  (setf *records* (nreverse *records*)))

;;; ---------------------------------------------------------------- 输出

(defun json-str (s)
  (with-output-to-string (o)
    (write-char #\" o)
    (loop for c across s do
      (case c (#\" (write-string "\\\"" o)) (#\\ (write-string "\\\\" o)) (t (write-char c o))))
    (write-char #\" o)))

(defun json-val (v)
  (cond ((stringp v) (json-str v))
        ((integerp v) (format nil "~d" v))
        ((listp v) (format nil "[~{~a~^,~}]" (mapcar #'json-val v)))
        (t (json-str (princ-to-string v)))))

(defun field-val (rec name)
  (cdr (assoc name (getf rec :fields) :test #'string-equal)))

(defun dump-json ()
  (format t "{~%")
  (loop for (rec . rest) on *records* do
    (format t "  ~a: {\"!superclasses\": [~a], \"Latency\": ~a, \"Resources\": ~a}~a~%"
            (json-str (getf rec :name))
            (json-str (first (getf rec :supers)))
            (json-val (field-val rec "Latency"))
            (json-val (field-val rec "Resources"))
            (if rest "," "")))
  (format t "}~%"))
