;; -*- mode: Clojure; coding: utf-8 -*-
;; Clojure file - http://clojure.org/
;; Leinigen project file - http:// FIXME
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

(defproject hb2posts-clj "1.0.0-SNAPSHOT"
  :description "Automation for my HTML and Handbook to blog author's tasks."
  :dependencies [[org.clojure/clojure "1.2.0"]
                 [org.clojure/clojure-contrib "1.2.0"]
                 [enlive "1.0.0"]])
