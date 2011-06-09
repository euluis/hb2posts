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

(defprotocol ValidatableType
  "Some validatable *type*.
This is a *big TODO*."
  (mandatory? [this field] "is field mandatory?")
  (type-hint [this field] "field's type hint, normally a symbol designating a Clojure's type, but can be a host Class. To be used as :tag is.")
  (validate [this] "validate. throws InvalidObjectException"))

;; A more advanced way to define cmd-line-option-spec type.
;; This is a *big TODO*. Probably using defrecord instead of
;; deftype is a better solution.
(deftype cmd-line-option-def [#^java.lang.String cmd-line-name
                              #^java.lang.String short-name
                              #^clojure.lang.Symbol value-type]
  ValidatableType
  (validate [this]
    ;;`TODO': it would be better if there would be an option in deftype
    ;;        to add the Validatable options in the field declaration...
    ;;        For instance mandatory field or not declaration,
    ;;        being optional the default.
    (if cmd-line-name
      :valid
      (throw (Exception. "cmd-line-option-def: name is mandatory")))))

(def *cmd-line-options* (ref [{:name "start-date" :type 'iso-date}
                              {:name "end-date" :type 'iso-date}]))

(def iso-date-re #"\d\d\d\d-[0-1]\d-[0-3]\d")

(defn create-cmd-line-option-key-re
  [{cl-name :name cl-short-name :short-name cl-type :type :as cmd-line-option}]
  [(keyword cl-name)
   (re-pattern (str "--" cl-name "[\\s+|=]("
                    iso-date-re ; TODO use cl-type
                    ")"))])

(defn cmd-line-options [cmd-line]
  (into {} (map (fn [[option-key option-re]]
                  (let [option-matcher (re-matcher option-re cmd-line)]
                    [option-key
                     (if-let [date (and (re-find option-matcher)
                                        (second (re-groups option-matcher)))]
                       date
                       (format-iso (today)))]))
                (map create-cmd-line-option-key-re @*cmd-line-options*))))
