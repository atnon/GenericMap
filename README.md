# GenericMap
Gaisler LEON3 top file parser and constant resolver. Very experimental.

This pretty much began as an effort to index what bus addresses, 
interrupt numbers were occupied when using the LEON3 and not wanting to traverse the GRMON output.

After that, things when south. Functionality is there, but not yet exposed in a very usable form.

That said, the script generates a dictionary containing all generic maps specified in the top file. 
Constants are resolved from the associated config.vhd, but resolution still need some more work to be complete.

The code is written with the [LEON3](http://www.gaisler.com/index.php/products/processors/leon3) in mind, but could be repurposed pretty easily. It should swallow most code, but without the added bells and whistles.

## Does

* Parse a given .vhd file into a python dictionary, which could be fairly useful.
* Contain quite a few hacks (the good, the bad, and the ugly).
* Possibly waste your time.
* Prohibit sleep.
* Seem to be the only tool of its kind. (Wouldn't have coded it otherwise)

## Does not

* Provide any actual output of direct use so far.
* Provide you any beer.
* Provide legal adivce.

## License
The code is licensed under the MIT License, so do what you like with the code. Pull requests are welcome!

The license in full can be read in the [LICENSE.md](LICENSE.md) file.
