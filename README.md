Relies heavily on [Selenium](https://selenium-python.readthedocs.io/)

Follow instructions here: [Windows Users](https://selenium-python.readthedocs.io/installation.html#detailed-instructions-for-windows-users)

Firefox requires [geckodriver](https://github.com/mozilla/geckodriver/releases)

To get a list of program switches, run with:

```bash
python sitesnipe.py --help
```

will result in the following:
```cmd
Duplicate park name: missinaibi provincial park
This program requires some information from the user.

Please type 'sitesnipe.py --help' for instructions
if any of your variables have a space in them, for example a campground/park with two words, YOU MUST ENCLOSE IN QUOTATION MARKS SO THE PROGRAM DOESN'T BREAK!!!
i.e. --campground 'LUNDY SOUTH' or -c middle creek
usage: sitesnipe.py [-h] -f FILE -a ARRIVAL_DATE -d DEPARTURE_DATE -e
                    {1,2,3,4,5,6,7} -p PARK -c CAMPGROUND -s SITE

Firefox Remote control to snipe Ontario Parks campsites.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Your username/password file, i.e. -f privateinfo.txt
  -a ARRIVAL_DATE, --arrival_date ARRIVAL_DATE
                        Date you arrive to the campground, format YYYY-MM-DD,
                        i.e. -a 2021-08-05
  -d DEPARTURE_DATE, --departure_date DEPARTURE_DATE
                        Date you leave the campground, format YYYY-MM-DD, i.e.
                        -d 2021-08-05
  -e {1,2,3,4,5,6,7}, --equipment {1,2,3,4,5,6,7}
                        Please enter a number 1 through 7 corresponding with
                        one of the following options for your equipment type.
                        The default is 6, trailer up to 32 feet (i.e. -e 6): 1
                        - Single Tent 2 - 2 Tents 3 - 3 Tents 4 - Trailer or
                        RV up to 18ft (5.5m) 5 - Trailer or RV up to 25ft
                        (7.6m) 6 - Trailer or RV up to 32ft (9.7m) [DEFAULT] 7
                        - Trailer or RV over 32ft (9.7m)
  -p PARK, --park PARK  The park you wish to book, i.e. -p wheatley
  -c CAMPGROUND, --campground CAMPGROUND
                        The park you wish to book, i.e. -c "Lumby South"
  -s SITE, --site SITE  The site you wish to book, i.e. -s 302
```

An example of running the program for the Wheatley Provincial Park, Highlands Campground, Site 67  August 3-4, 2021 with
a trailer under 18 feet would be:

```bash
python sitesnipe.py -f privateinfo.txt -a 2021-08-03 -d 2021-08-04 -e 4 -p wheatley -c Highlands -s 67
```

Place your Ontario Parks username and password on separate lines in a text file and call that file in the switches 
listed above.  In this case, I called it `privateinfo.txt`.  There's an example file you can rename and modify called 
`example_privateinfo.txt` in the repo. 