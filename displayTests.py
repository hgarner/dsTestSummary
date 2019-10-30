from lxml import etree
import argparse
import os

##
# parse junit xml output from R testthat tests
# print summary tests and counts of passed/failed/etc
##

# process the input_filename and return an etree object
# @param string input_filename - path of junit xml file to process
# @return object etree
def process_input(input_filename):
  if not os.path.isfile(input_filename):
    raise ValueError(f'input {input_filename} does not appear to exist')

  with open(input_filename, 'r') as input_file:
    test_results = etree.parse(input_file)

  return test_results

# get all the testsuites from the test_results (etree ElementTree)
# @param etree ElementTree of test results
# @return list of etree Elements (testsuite)
def get_testsuites(test_results):
  testsuite_xpath = '//testsuite'
  testsuites = test_results.xpath(testsuite_xpath)
  return testsuites

# process a testsuite Element and print its name (format dependent on nesting)
# then print successes/failures if tests > 0
# @param etree Element testsuite
# @param dict test_result_count (default None)
# @return dict count of results of tests
def print_results(testsuite, test_result_count = None):
  # if test_result_count is None, this is the first run,
  # so setup the counter dict and print the column headers
  if test_result_count is None:
    print(f' OK| Fd| Sk|Err')
    test_result_count = {
      'tests': 0,
      'succeeded': 0,
      'skipped': 0,
      'failed': 0,
      'errors': 0
    }
  testsuite_name = testsuite.attrib['name']
  num_tests = int(testsuite.attrib['tests'])
  test_result_count['tests'] += num_tests
  if num_tests > 0:
    failed = int(testsuite.attrib['failures'])
    errors = int(testsuite.attrib['errors'])
    skipped = int(testsuite.attrib['skipped'])
    test_result_count['failed'] += failed
    test_result_count['errors'] += errors
    test_result_count['skipped'] += skipped
    # ok should equal num_tests - (failed + skipped + errors)
    # note - check if this is correct!
    ok = num_tests - (failed + skipped + errors)
    test_result_count['succeeded'] += ok
    print(f'{ok:>3}|{failed:>3}|{skipped:>3}|{errors:>3} {testsuite_name}')
  else:
    # if num_tests is 0, then this is a header row
    print(f'{testsuite_name}')
  return test_result_count

if __name__ == '__main__':
  # run the parser and print output of tests
  # using the provided input filename (junit xml)
  parser = argparse.ArgumentParser(description = 'Process junit test output and display to console')
  parser.add_argument('--input', dest = 'input_filename', help = 'filename of junit file to parse')
  args = parser.parse_args()
  print(f'Parsing junit file {args.input_filename}')

  test_results = process_input(args.input_filename)
  testsuites = get_testsuites(test_results)
  test_result_count = None
  for testsuite in testsuites:
    test_result_count = print_results(testsuite, test_result_count)
  print(f'''
    Results:
      Tests:     {test_result_count['tests']:>4}
      Succeeded: {test_result_count['succeeded']:>4}
      Skipped:   {test_result_count['skipped']:>4}
      Failed:    {test_result_count['failed']:>4}
      Errors:    {test_result_count['errors']:>4}
  ''')
