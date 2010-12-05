(defn say-hello [name] 
  (println "Hello," name))

(defn pig-lagtin [word] 
  (let [first-letter (first word)] 
    (if 
      ((vowel? first-letter)) 
      (str word "ay") 
      (str (subs word 1) first-letter "ay"))))

(defn parting 
  ([] (parting "World")) 
  ([name] (parting name "en")) 
  ([name language] 
    (condp = language 
      (str "Goodbye, " name) 
      (str "Adios, " name) 
      (throw (IllegalArgumentException 
        (str "unsupported language " language)))))

(defn factorial-1 
  ("computes the factorial of a positive integer in a way that doesn't consume stack space") [number] 
  (loop [n number factorial 1] 
    (if (zero? n) factorial 
      (recur (dec n) (* factorial n)))))

(defn reverse 
  ("Returns a seq of the items in coll in reverse order. Not lazy.") [col1] 
  (reduce conj nil col1))