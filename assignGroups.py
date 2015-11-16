#!/usr/bin/env python
import csv, os, sys, re

uid_rx = re.compile(r"""
  .*-\s*(?P<uid>([a-z]{2}[0-9]{4,5})|([a-z]{5,6}))$
""", re.M | re.X)

class Groups:
  kaggle = 1
  quiz = 1
  spam = 1
  research = 1

  groups = {}

  def addToGroup(self, uid, tag, pair=False):
    # check whether person is already assigned to a group
    if uid in self.groups:
      return

    if tag == 'k':
      rw = "Kaggle%02d" % self.kaggle
      self.kaggle += 1
    elif tag == 's':
      rw = "Spam%02d" % self.spam
      self.spam += 1
    elif tag == 'q':
      rw = "Quiz%02d" % self.quiz
      self.quiz += 1
    elif tag == 'r':
      rw = "Resrch%02d" % self.research
      self.research += 1
    else:
      sys.error("Group tag: " + tag + " not recognised")
    self.groups[uid] = rw
    if pair:
      self.groups[pair] = rw

  def getGroups(self):
      return self.groups

  def getGroupsList(self):
    d = []
    for i in range(1, 41):
      d.append("Kaggle%02d" % i)
      d.append("Spam%02d" % i)
      d.append("Quiz%02d" % i)
      d.append("Resrch%02d" % i)
    d.sort()
    d = ['NotAllocated'] + d
    return d

if __name__ ==  '__main__':
  if len(sys.argv) < 2:
    sys.exit('Usage: %s student csv file from Google Spreadsheet' % sys.argv[0])
  if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: File %s was not found!' % sys.argv[1])
  fname = sys.argv[1].find('.csv')
  if fname == -1:
    sys.exit('Input file must have *.csv* extension')
  else:
    fname = sys.argv[1][:fname]

  database = []
  with open(sys.argv[1], 'r') as csvfile:
    choices = csv.reader(csvfile)
    for row in choices:
      uid = uid_rx.search(row[1].lower().strip())
      if uid:
        uid = uid.group(1).strip()
      else:
        print('User id not found for row: %s' % ','.join(row))
        print('Skipping this row')
        continue

      option = row[2].lower().strip()
      if 'kaggle' in option:
          option = 'k'
      elif 'spam' in option:
        option = 's'
      elif 'quiz' in option:
        option = 'q'
      elif 'research' in option:
        option = 'r'
      else:
        print('User option not recognised for row: %s' % ','.join(row))
        print('Setting choice to \'#\'\n')
        option = '#'

      partner = uid_rx.search(row[3].lower().strip())
      if partner:
        partner = partner.group(1).strip()
      else:
        partner = ''

      database.append( (uid, option, partner) )

  # check whether pairs match
  for i in database:
    if i[2] != '':
      irev = i[::-1]
      if irev not in database:
        print( 'person: ' + str(i[0]) + ' declared a pair: ' + str(i) + ' but person: ' + str(i[2]) + " did not")

  # generate group assignment
  gg = Groups()
  for i in database:
    gg.addToGroup(i[0], i[1], i[2])

  # generate SAFE file
  gas = gg.getGroups()
  with open(fname + '_groupsAssignment' + '.csv', 'w') as outcsv:
    safe = csv.writer(outcsv)
    safe.writerow(["Student", "Groups"])
    for i in gas:
      safe.writerow([i, gas[i]])

  with open(fname + '_groupsList' + '.csv', 'w') as outg:
    d = gg.getGroupsList()
    outg.write("\n".join(d))
