(in-package :cl-user)
(load "mini-tbl.lisp")

(mini-tbl:run
 '((class WriteRes (res) ()
     (Resources list res)
     (Latency int 1))

   (def ALU0 (WriteRes ("P73IALU")) ((Latency 2)))

   (multiclass LoadStore (lat)
     (def _LD (WriteRes ("P23LD")) ((Latency lat)))
     (def _ST (WriteRes ("P4ST")) ((Latency lat))))

   (defm MEM (LoadStore 4))

   (def :anon (WriteRes ("P0")) ())))

(mini-tbl:dump-json)
