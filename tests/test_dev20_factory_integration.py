"""Author integration for production request→factory composition.

Only OS/authority lower ports are replaced. The production request entry,
native_session factory, SessionRunner, NativeDriver and Coordinator are real.
This is author evidence, never native Windows/LAB/SITE validation.
"""
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from helpers import authority_case, SID
from test_dev4_recovery import extend
from aifilm_p00.session import SessionRunner
from aifilm_p00.admission import Coordinator
from aifilm_p00.native.session_driver import NativeDriver
from aifilm_p00.native.request_entry import prepare_execution


class ProductionFactoryCompositionTests(unittest.TestCase):
    def prepared(self, interface, purpose):
        _, plan, _, request_store = authority_case(purpose)
        request_store, ref = extend(request_store, 'execution_plan',
            {'schema_version': 1, 'withdrawn': False, 'plan': plan})

        api = object()
        native_store = SimpleNamespace(operators=frozenset({SID}), host_id='synthetic-host')
        guard = object(); paths = object(); journal = object(); supervisor = object(); system = object()
        req = 'aifilm_p00.native.request_entry.'
        drv = 'aifilm_p00.native.session_driver.'
        with patch(req+'_entry', return_value=(None, request_store, None, None, None)), \
             patch(drv+'_entry', return_value=(api, native_store, None, None, None)), \
             patch(drv+'WindowsPaths', return_value=paths), \
             patch(drv+'NativeGuard', return_value=guard), \
             patch(drv+'NativeJournal', return_value=journal), \
             patch(drv+'NativeSupervisor', return_value=supervisor) as supervisor_factory, \
             patch(drv+'NativeSystemState', return_value=system):
            actual_plan, session = prepare_execution('/workspace/synthetic', interface, ref)
        supervisor_factory.assert_called_once_with(api, paths, guard, require_executable_trust=True)
        return plan, actual_plan, session, (guard, paths, journal, supervisor, system)

    def test_request_entry_composes_real_production_factory_for_supported_interfaces(self):
        for interface, purpose in (
            ('apply', 'CREATE'),
            ('verify', 'SITE_VERIFY'),
            ('support-bundle', 'SUPPORT_BUNDLE'),
            ('verify', 'RECONCILIATION_ONLY'),
        ):
            with self.subTest(interface=interface, purpose=purpose):
                expected, actual, session, lower = self.prepared(interface, purpose)
                guard, paths, journal, supervisor, system = lower
                self.assertEqual(actual, expected)
                self.assertIs(type(session), SessionRunner)
                self.assertIs(type(session.driver), NativeDriver)
                self.assertIs(type(session.coordinator), Coordinator)
                self.assertIs(session.driver.paths, paths)
                self.assertIs(session.driver.supervisor, supervisor)
                self.assertIs(session.driver.system, system)
                self.assertIs(session.coordinator.guard, guard)
                self.assertIs(session.coordinator.storage, journal)
                self.assertEqual(session.driver.operators, frozenset({SID}))


if __name__ == '__main__':
    unittest.main()
