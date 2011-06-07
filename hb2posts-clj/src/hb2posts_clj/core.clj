;; -*- mode: Clojure; coding: utf-8 -*-
;; Clojure file - http://clojure.org/
;; By Luis Sergio Oliveira a command line utility to extract blog posts from my
;; digital programming handbook.

;; Copyright (c) 2011 Contributors - see below
;; All rights reserved.
;; The use and distribution terms for this software are covered by the
;; Eclipse Public License 1.0 (http://opensource.org/licenses/eclipse-1.0.php)
;; which can be found in the file epl-v10.html at the root of this distribution.
;; By using this software in any fashion, you are agreeing to be bound by
;; the terms of this license.
;; You must not remove this notice, or any other, from this software.
;; Contributors:
;; - Luis Sergio Oliveira (euluis)

(ns hb2posts-clj.core
  (:import (java.io File)
           (java.util Calendar Date)))

(defn hb-file-name [file-name]
  (.getName (File. file-name)))

(defn format-2d [n]
  (if (>= n 10) (str n) (str "0" n)))

(defn today [] (Date.))

;;; WTF, Java doesn't have this!?!
(defn format-iso [d]
  (let [calendar (Calendar/getInstance)]
    (str (. calendar get Calendar/YEAR) "-"
         ;; WTF, stupid and wrong implementation!
         (format-2d (+ 1 (. calendar get Calendar/MONTH))) "-"
         (format-2d (. calendar get Calendar/DAY_OF_MONTH)))))

(defn cmd-line-options [cmd-line]
  (into {} (map (fn [[option-key option-re]]
                  (let [option-matcher (re-matcher option-re cmd-line)]
                    [option-key
                     (if (re-find option-matcher)
                       (second (re-groups option-matcher))
                       (format-iso (today)))]))
                [[:start-date #"--start-date\s+(\d\d\d\d-\d\d-\d\d)"]
                 [:end-date #"--end-date\s+(\d\d\d\d-\d\d-\d\d)"]])))
