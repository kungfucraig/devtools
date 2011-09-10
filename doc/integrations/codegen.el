;;;
;;; A few simple interactive emacs functions that integrate with codegen
;;;


(defun cpp-source-file-header (fileName)
  (interactive "bBuffer Name: ")
  (shell-command (concat "cg cs -m classname="
								 (if (string= (substring fileName -2) "qh")
									  (substring fileName 0 -3)
									  (substring fileName 0 -2))
								 )
					  1
					  )
  )


(defun cpp-include-file-header (fileName) 
  (interactive "bBuffer Name: ")
  (shell-command (concat "cg ch -m classname="
								 (if (string= (substring fileName -2) "qh")
									  (substring fileName 0 -3)
  									(substring fileName 0 -2))
								 )
					  1
					  )
  (beginning-of-buffer))


(defun cpp-function-header ()
  (interactive)
  (shell-command (concat "cg cf") 1))
