;;; .emacs --- Minimal rice entry point -*- lexical-binding: t; -*-
;; Existing Customize settings are kept in their own file.
(setq custom-file (expand-file-name "custom.el" user-emacs-directory))
(when (file-exists-p custom-file)
  (load custom-file nil t))
(load (expand-file-name "rice-appearance.el" user-emacs-directory) nil t)

(load (expand-file-name "rice-completion.el" user-emacs-directory) nil t)

(load (expand-file-name "rice-dashboard.el" user-emacs-directory) nil t)
