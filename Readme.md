# Assign groups to students automatically #
Download your Google spreadsheet as a `.csv` and your student list and run:
``` BASH
./assignGroups.py ./coms20201choices.csv ./students.csv
```

Student list should be in form:
```
User,*****
ab12345,*****
ba54321,*****
```
where `*****` can be empty or another column in the file.
