#!/usr/bin/python2.7 
__AUTHOR__='Danevych V.'
__COPYRIGHT__='Danevych V. 2015 Kiev, Ukraine'
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

try:
  import cx_Oracle
except ImportError,info:
  print "Import Error:",info
  sys.exit()

import sys
import subprocess as sub


#Define constant
#EMAIL_TO='vitaliy.danevych@life.com.ua'
EMAIL_TO='oss_group@life.com.ua'

  
if cx_Oracle.version<'4.0':
  print "Very old version of cx_Oracle :",cx_Oracle.version
  sys.exit()


def send_email(error_type, theme, text):
  command = 'echo "%s" | mail -s "%s" %s' % (text, theme, EMAIL_TO)
  try:
    retcode = sub.call(command, shell=True) #sends email
    if retcode < 0:
      print >>sys.stderr, "Child was terminated by signal", -retcode
    else:
      print >>sys.stderr, "Child returned", retcode
      print "Email was sent"
  except OSError as e:
      print >>sys.stderr, "Execution failed:", e
      print "Email was not sent due an internal error"
  print 'command: ', command
  #print 'error_type: ', error_type, 'theme: ', theme, 'text:', text #only for debugging
  print 'retcode: ', retcode
  exit(0)


def connection(db_user,db_passwd,db_host_sid):
  global con  
  try:
    con = cx_Oracle.connect(db_user, db_passwd, db_host_sid)
  except cx_Oracle.DatabaseError,info:
    print "Logon  Error:",info
    theme = "Huawei PRS DB connection problem"
    text = """PRS system checker has detected issue related to DB connection.
    Please, check PRS DB on IP %s
    Oracle login and password are available in KeyPass.
    The error code: %s
    \\\BR
    Yours PRS script-checker
    """ % ('10.3.16.20', info)
    send_email(1, theme, text)
    exit(1) # send email about DB connection problem and exit
  vers = con.version.split('.')  #Execute it if all is ok
  print "Oracle client version: ", con.version
  if vers[0] == '10':
    print "Running 10g"
  elif vers[0] == '11':
    print "Running 11g"
  elif vers[0] == '12':
    print "Running 12"


def select(sql):
  #connection('sqlex','passwd4user','ora-test:1521/orcl')
  connection('readonly','readonly_739','10.3.16.20:1521/prsdb')
  my_cursor = con.cursor()
  try:
    my_cursor.execute(sql)
  except cx_Oracle.DatabaseError,info:
    print "SQL Error:",info
    theme = "Huawei PRS DB sql-execution problem"
    text = """PRS system checker has detected error during control sql execution.
    Please, check what is the reason. PRS DB IP %s
    Oracle login and password are available in KeyPass.
    The  error code: %s
    \\\BR
    Yours PRS script-checker
    """ % ('10.3.16.20', info)
    send_email(1, theme, text)
    exit(1)
  print "start table"
  try:
    for result in my_cursor.fetchone():  # if succesfully found value, so if data at PRS DB is up-to-date
      print "result is:", result
  except TypeError, info: # nothing found and in this case
    print "oops! result is not set! missing data at PRS DB!"
    theme = "Huawei PRS DB data is not up-to-date!"
    text = """PRS system checker has detected data at PRS Database is not up-to-date!
    Please, check what is the reason. PRS DB IP %s
    Oracle login and password are available in KeyPass.
    The  error code: %s (it means no fresh data at database)
    \\\BR
    Yours PRS script-checker
    """ % ('10.3.16.20', info)
    send_email(1, theme, text)
  print "end table"  
  #print "bindnames: ",my_cursor.bindnames()
  con.close()


#Declare Main function
def main():
  print "Python cx_Oracle.version of module: ",cx_Oracle.version
  #sql = """
  #SELECT a.name, a.class, a.launched
  #FROM ships a 
  #"""
  sql = """
  SELECT a.resulttime
  FROM prscommdb.t_houraggrtime a
  where a.resulttime >= sysdate - 1/8
  """
  select(sql)

  
#Execute Main function 
if __name__ == '__main__':
  main()
  
  
