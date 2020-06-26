;;; Directory Local Variables
;;; For more information see (info "(emacs) Directory Variables")

((nil .
      ((eval .
	     (set (make-local-variable 'org-attach-id-dir)
		  (expand-file-name ".artifacts"
				    (locate-dominating-file default-directory ".dir-locals.el"))))
       (eval .
	     (set (make-local-variable 'org-directory)
		  (expand-file-name ".status"
				    (locate-dominating-file default-directory ".dir-locals.el"))))
       )))
