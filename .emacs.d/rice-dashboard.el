;;; rice-dashboard.el --- Startup homepage -*- lexical-binding: t; -*-

(require 'package)
(package-initialize)
(require 'recentf)
(require 'project)
(require 'dashboard)

(recentf-mode 1)

(setq dashboard-banner-logo-title "Welcome Home..."
      dashboard-startup-banner 3
      dashboard-center-content t
      dashboard-show-shortcuts t
      dashboard-set-heading-icons nil
      dashboard-set-file-icons nil
      dashboard-set-footer nil
      dashboard-projects-backend 'project-el
      dashboard-items '((recents . 5)
                        (agenda . 5)
                        (bookmarks . 5)
                        (projects . 5)
                        (registers . 5)))

(when (facep 'dashboard-heading)
  (set-face-attribute 'dashboard-heading nil
                      :foreground "#d46a50"
                      :weight 'normal
                      :slant 'italic))

(dashboard-setup-startup-hook)
