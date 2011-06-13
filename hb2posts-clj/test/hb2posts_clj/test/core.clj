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

(deftest cmd-line-options-start-end-dates-test
  (testing "that cmd-line-options correctly processes start and end dates"
    (are [expected-start-date expected-end-date cmd-line]
         ;; FIXME: difficult to understand what went wrong when fails
	 (let [{start-date :start-date end-date :end-date
                :as options} (cmd-line-options cmd-line)
                ;; FIXME: the following use of fn today is fragile around midnight
                ;; TODO: an idea is to stub today implementation.
                ;;       tried the following at top level without success
                ;; (in-ns 'hb2posts-clj.core)
                ;; (def today (fn [] "0000-01-01"))
                ;; (in-ns 'hb2posts-clj.test.core)
                ;; with the test
                ;; :today :today "--start-date=0000-01-01"
               today-val (format-iso (today))
               [actual-start-date actual-end-date] (map #(if (= today-val %) :today %)
                                                        [start-date end-date])]
	   (and (= expected-start-date actual-start-date)
		(= expected-end-date actual-end-date)))
	 "2010-01-01" "2011-01-01" "--start-date 2010-01-01 --end-date 2011-01-01"
         :today :today ""
         "2010-01-01" "2011-01-01" "--end-date 2011-01-01 --start-date 2010-01-01"
         :today "2010-01-01" "--end-date=2010-01-01"
         ;; see TODO above, which this test replaces temporarily  
         :today :today (str "--start-date=" (format-iso (today)))
         "2010-12-31" "2011-01-01" "-s 2010-12-31 -e 2011-01-01")))

(deftest cmd-line-options-handbook-test
  (testing "that cmd-line-options correctly processes handbook option"
    ;; TODO: add tests for invalid handbook option value
    (are [expected-hb cmd-line]
         (= expected-hb (:handbook (cmd-line-options cmd-line)))
         "programacao" ""
         "programacao" "-b programacao"
         "idiota" "--handbook=idiota")))
