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
  (:use [clojure.test])
  (:import (java.util Calendar Date)))

(deftest basic-file-name-fns
  (testing "that hb-file-name will return the correct file names"
    (are [expected-file-name file-name]
	 (= expected-file-name (hb-file-name file-name))
	 "filename.html" "filename.html"
	 "x.y" "/foo/bar/x.y"
	 "name.ext" "../foo/bar/name.ext"
	 "name" "/absolute/path/name")))

(defn format-2d [n]
  (if (>= n 10) (str n) (str "0" n)))

;;; WTF, Java doesn't have this!?!
(defn format-iso [d]
  (let [calendar (Calendar/getInstance)]
    (str (. calendar get Calendar/YEAR) "-"
         ;; WTF, stupid and wrong implementation!
         (format-2d (+ 1 (. calendar get Calendar/MONTH))) "-"
         (format-2d (. calendar get Calendar/DAY_OF_MONTH)))))

(deftest hb2post-cmd-line-options
  (testing "that cmd-line-options correctly processes start and end dates"
    (are [expected-start-date expected-end-date cmd-line]
	 (let [{start-date :start-date end-date :end-date :as options}
	       (cmd-line-options cmd-line)]
	   (and (= expected-start-date start-date)
		(= expected-end-date end-date)))
	 "2010-01-01" "2011-01-01" "--start-date 2010-01-01 --end-date 2011-01-01"
         ;; FIXME: difficult to understand what went wrong when fails
         ;; FIXME: fragile around midnight
         ;; TODO: in cmd-line-options default start date and end date are today's date
         (format-iso (Date.)) (format-iso (Date.)) "")))
