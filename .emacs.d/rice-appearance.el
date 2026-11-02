;;; rice-appearance.el --- Reference-inspired rice styling -*- lexical-binding: t; -*-

;; Appearance only: no package downloads, shell changes, or new keybindings.
(require 'org)

(deftheme rice-gruvbox "Near-black/tan palette with reference-inspired Org faces.")

(let ((bg "#000200")
      (fg "#e9d9b6")
      (khaki "#ba9f64")
      (green "#6b9e67")
      (blue "#85a699")
      (pink "#a86585")
      (orange "#edbb26")
      ;; A brighter red-orange for readable headings, not an exact sampled color.
      (heading-red "#d46a50"))
  (custom-theme-set-faces
   'rice-gruvbox
   `(default ((t (:background ,bg :foreground ,fg))))
   `(cursor ((t (:background ,orange))))
   `(fringe ((t (:background ,bg :foreground ,khaki))))
   `(vertical-border ((t (:foreground "#4b5143"))))
   `(region ((t (:background ,khaki :foreground ,bg))))
   `(highlight ((t (:background "#20271d"))))
   `(hl-line ((t (:background "#11170f"))))
   `(minibuffer-prompt ((t (:foreground ,green :weight bold))))
   `(link ((t (:foreground ,green :underline t))))
   `(link-visited ((t (:foreground ,pink :underline t))))
   `(shadow ((t (:foreground "#918b78"))))
   `(error ((t (:foreground ,heading-red :weight bold))))
   `(warning ((t (:foreground ,orange))))
   `(success ((t (:foreground ,green))))
   `(font-lock-comment-face ((t (:foreground "#918b78" :slant italic))))
   `(font-lock-comment-delimiter-face ((t (:inherit font-lock-comment-face))))
   `(font-lock-string-face ((t (:foreground ,green))))
   `(font-lock-keyword-face ((t (:foreground ,heading-red :slant italic))))
   `(font-lock-function-name-face ((t (:foreground ,blue))))
   `(font-lock-variable-name-face ((t (:foreground ,fg))))
   `(font-lock-type-face ((t (:foreground ,pink))))
   `(font-lock-constant-face ((t (:foreground ,orange))))
   `(font-lock-builtin-face ((t (:foreground ,khaki))))
   `(isearch ((t (:background ,orange :foreground ,bg))))
   `(lazy-highlight ((t (:background ,green :foreground ,bg))))
   `(show-paren-match ((t (:background "#304536" :foreground ,fg :weight bold))))
   `(mode-line ((t (:background ,bg :foreground ,khaki :box nil
                   :overline "#5c6250" :height 0.9))))
   `(mode-line-inactive ((t (:background ,bg :foreground "#918b78" :box nil
                            :overline "#343a30" :height 0.9))))
   `(mode-line-buffer-id ((t (:foreground ,fg :weight bold))))
   `(header-line ((t (:background ,bg :foreground ,khaki :box nil))))
   `(org-document-title ((t (:foreground ,blue :height 1.5 :weight normal))))
   `(org-document-info ((t (:foreground ,khaki))))
   `(org-level-1 ((t (:foreground ,blue :height 1.35 :weight normal :slant normal))))
   `(org-level-2 ((t (:foreground ,pink :height 1.15 :weight normal :slant italic))))
   `(org-level-3 ((t (:foreground ,heading-red :height 1.0 :weight normal :slant italic))))
   `(org-level-4 ((t (:foreground ,green :height 1.0 :weight normal :slant italic))))
   `(org-level-5 ((t (:foreground ,khaki :height 1.0 :weight normal))))
   `(org-level-6 ((t (:foreground ,blue :height 1.0 :weight normal))))
   `(org-level-7 ((t (:foreground ,pink :height 1.0 :weight normal))))
   `(org-level-8 ((t (:foreground ,green :height 1.0 :weight normal))))
   `(org-link ((t (:foreground ,green :underline t))))
   `(org-todo ((t (:foreground ,heading-red :weight bold))))
   `(org-done ((t (:foreground ,green :weight normal))))
   `(org-date ((t (:foreground ,khaki :background "#1c2119" :height 0.9))))
   `(org-meta-line ((t (:foreground "#918b78" :slant italic :height 0.9))))
   `(org-special-keyword ((t (:foreground ,khaki :height 0.9))))
   `(org-property-value ((t (:foreground "#a49a81" :height 0.9))))
   `(org-drawer ((t (:foreground ,khaki :height 0.9))))
   `(org-block ((t (:background "#10160e" :foreground ,fg))))
   `(org-block-begin-line ((t (:background "#10160e" :foreground ,khaki :slant italic))))
   `(org-block-end-line ((t (:inherit org-block-begin-line))))
   `(org-code ((t (:foreground ,khaki))))
   `(org-verbatim ((t (:foreground ,orange))))
   `(org-quote ((t (:foreground ,khaki :slant italic))))
   `(org-ellipsis ((t (:foreground ,heading-red :underline nil))))))

(mapc #'disable-theme custom-enabled-themes)
(enable-theme 'rice-gruvbox)

;; Minimal window chrome; Hyprland supplies the gradient window border.
(when (fboundp 'menu-bar-mode) (menu-bar-mode -1))
(when (fboundp 'tool-bar-mode) (tool-bar-mode -1))
(when (fboundp 'scroll-bar-mode) (scroll-bar-mode -1))
(when (fboundp 'blink-cursor-mode) (blink-cursor-mode -1))
(setq inhibit-startup-screen t
      initial-scratch-message nil
      ring-bell-function #'ignore
      frame-title-format '("%b — Emacs"))
(setq-default cursor-type 'box
              line-spacing 2
              left-margin-width 2
              right-margin-width 2)

(defun rice-configure-frame (&optional frame)
  "Set font and framing for FRAME, including future graphical frames."
  (with-selected-frame (or frame (selected-frame))
    (when (display-graphic-p)
      (set-frame-parameter nil 'internal-border-width 6)
      (set-frame-parameter nil 'left-fringe 6)
      (set-frame-parameter nil 'right-fringe 6)
      (when (find-font (font-spec :family "JetBrainsMono Nerd Font"))
        (set-face-attribute 'default nil :family "JetBrainsMono Nerd Font" :height 120)))))
(add-hook 'after-make-frame-functions #'rice-configure-frame)
(rice-configure-frame)

;; Built-in Org only. Package-based bullets/dashboard can be added separately.
(setq org-hide-emphasis-markers t
      org-hide-leading-stars t
      org-pretty-entities t
      org-ellipsis " ▾"
      org-startup-indented t
      org-fontify-quote-and-verse-blocks t)
(add-hook 'org-mode-hook #'visual-line-mode)
(add-hook 'org-mode-hook #'org-indent-mode)

(provide 'rice-appearance)
;;; rice-appearance.el ends here
