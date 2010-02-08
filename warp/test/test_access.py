from twisted.trial import unittest

from warp.common import access as a

class AccessTest(unittest.TestCase):

    def testAllowDeny(self):
        self.assertEqual(a.Allow().allows(object()), True)
        self.assertEqual(a.Deny().allows(object()), False)

    def testEquals(self):
        obj = object()
        self.assertEqual(a.Equals(obj).allows(obj), True)
        self.assertEqual(a.Equals(obj).allows(object()), False)
        
    def testCallback(self):
        self.assertEqual(a.Callback(lambda _: True).allows(object()), True)
        self.assertEqual(a.Callback(lambda _: False).allows(object()), False)

    def testCombiners(self):
        self.assertEqual(a.All(a.Allow(), a.Allow()).allows(object()), True)
        self.assertEqual(a.All(a.Allow(), a.Deny()).allows(object()), False)       
        self.assertEqual(a.Any(a.Deny(), a.Allow()).allows(object()), True)
        self.assertEqual(a.Any(a.Deny(), a.Deny()).allows(object()), False)
        
    def testEmptyRole(self):
        self.assertEqual(a.Role({}).allows(object()), None)

    def testEmptyRuleList(self):
        obj = object()
        self.assertEqual(a.Role({obj: []}).allows(obj), None)
        
    def testRoleAllows(self):
        obj = object()
        self.assertEqual(a.Role({obj: [a.Allow()]}).allows(obj), True)

    def testRoleDenies(self):
        obj = object()
        self.assertEqual(a.Role({obj: [a.Deny()]}).allows(obj), False)

    def testRoleDefaults(self):
        self.assertEqual(a.Role({}, default=[a.Allow()]).allows(object()), True)
        self.assertEqual(a.Role({}, default=[a.Deny()]).allows(object()), False)
        self.assertEqual(a.Role({}, default=[]).allows(object()), None)
