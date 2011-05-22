;; -*- mode: Clojure; coding: utf-8 -*-
;; Clojure file - http://clojure.org/

;; Automated tests for hb2posts-clj project.

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

(ns hb2posts-clj.test.core
  (:use [hb2posts-clj.core] :reload)
  (:use [clojure.test]))

(deftest basic-file-name-fns
  (testing "that hb-file-name will return the correct file names"
    (are [expected-file-name file-name]
	 (= expected-file-name (hb-file-name file-name))
	 "filename.html" "filename.html"
	 "x.y" "/foo/bar/x.y"
	 "name.ext" "../foo/bar/name.ext"
	 "name" "/absolute/path/name")))
