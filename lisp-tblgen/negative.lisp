(load "mini-tbl.lisp")
(mini-tbl:run
 '((class WriteRes (res) ()
     (Resources list res)
     (Latency int 1))
   (def Bad (WriteRes ("P0")) ((Latency "two")))))
