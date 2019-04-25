.. image:: https://img.shields.io/pypi/v/idris-python.svg
    :target: https://pypi.python.org/pypi/idris-python

idris-cam
==============

Finally, we reached dependent types in Python community.

Install
================


```
pip install idris-python
```

Usage
====================


- Command: Idris-Python

.. image:: https://raw.githubusercontent.com/thautwarm/idris-python/master/cmd-idris-python.png
    :width: 90%
    :align: center


- Command: Run-Cam

.. image:: https://raw.githubusercontent.com/thautwarm/idris-python/master/cmd-run-cam.png
    :width: 90%
    :align: center

## Example

Quite verbose for the lack of encapsulations, not a good example but I'm so busy..

Following example just revealed that I've alredy implmented such a big task.

.. code-block :: idris

    module Main
    import Cam.FFI
    import Cam.IO
    import Cam.Data.Collections
    import Cam.Data.FCollections
    import Cam.Data.Compat
    import Data.Vect
    import Data.HVect

    %access export

    main : IO ()
    main = do
        putStrLn $ show vect
        sklearn   <- camImport $ TheModule "sklearn.datasets"
        load_iris <- camImportFrom sklearn "load_iris"
        iris      <- unsafeCall load_iris $ zero_ary
        data'     <- getattr iris "data"
        tag       <- getattr iris "target"
        rfc       <- let ensemble = camImport $ TheModule "sklearn.ensemble" in
                     camImportFrom !ensemble "RandomForestClassifier"
        clf       <- unsafeCall rfc zero_ary
        fit       <- getattr clf "fit"
        unsafeCall fit . unsafe $ the (FList _) [data', tag]
        score <- getattr clf "score"
        value <- unsafeCall score . unsafe $ the (FList _) [data', tag] -- overfit
        println value
      where
        vect : HVect [Int]
        vect = the (HVect _) [1]

        zero_ary : Unsafe
        zero_ary = unsafe $  the (FList Unsafe) $ []

        getattr' : IO Unsafe
        getattr' = do
            b <- camImport $ TheModule "builtins"
            camImportFrom b "getattr"

        getattr : Unsafe -> String -> IO Unsafe
        getattr obj s =
            let s = unsafe . the (Boxed String) $ s in
            let args = unsafe . the (FHVect [_, _]) $ [obj, toText s] in
            unsafeCall !getattr' args


You might got

.. code ::

   [1]
   0.99

If you run it as a file with command ``idris-python``.
