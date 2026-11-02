;;; rice-completion.el --- Minibuffer completion -*- lexical-binding: t; -*-

(require 'package)
(package-initialize)
(require 'vertico)

(setq vertico-count 8
      vertico-resize nil
      vertico-cycle t)

(vertico-mode 1)

(set-face-attribute 'vertico-current nil
                    :background "#817667"
                    :foreground "#000200")

(provide 'rice-completion)
