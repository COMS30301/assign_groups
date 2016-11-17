#!/usr/bin/env python
import csv, os, sys, re

uid_rx = re.compile(r"""
  .*-\s*(?P<uid>([a-z]{2}[0-9]{4,5})|([a-z]{5,6}))$
""", re.M | re.X)
ui_rx = re.compile(r"""
  (?P<uid>([a-z]{2}[0-9]{4,5})|([a-z]{5,6}))
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

  # read in usernames downloaded form FEN
  uids = []
  with open(sys.argv[2], 'r') as usernames:
    u = csv.reader(usernames)
    for i in u:
      if not i:
        continue
      uid = ui_rx.search(i[0].lower().strip())
      if uid:
        uid = uid.group(1).strip()
        uids.append(uid)

  database = []
  with open(sys.argv[1], 'r') as csvfile:
    choices = csv.reader(csvfile)
    for row in choices:
      uid = uid_rx.search(row[2].lower().strip())
      if uid:
        uid = uid.group(1).strip()
      else:
        print('User id not found for row: %s' % ','.join(row))
        print('Skipping this row')
        continue

      option = row[3].lower().strip()
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

      partner = uid_rx.search(row[4].lower().strip())
      if partner:
        partner = partner.group(1).strip()
      else:
        partner = ''

      database.append( (uid, option, partner) )

  # remove duplicates form the database
  database = list(set(database))

  # check whether pairs match
  loners = []
  for i in database:
    uids.remove(i[0])
    if i[2] == '':
      if i[1] != 'q' and i[1] != 'r':
        print( 'person: ' + str(i[0]) + ' did not declare a pair for *' + i[1] + '* assignment')
        loners_uid.append(i[0])
        loners_choice.append(i[1])
    else:
      irev = i[::-1]
      if irev not in database:
        print( 'person: ' + str(i[0]) + ' declared a pair: ' + str(i) + ' but person: ' + str(i[2]) + " did not")

  # loners_uid/choice - list of people without partner
  # uids - list of people who have not submitted anything

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
