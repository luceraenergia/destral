import logging
import unittest

from destral.openerp import OpenERPService
from destral.transaction import Transaction
from osconf import config_from_environment


logger = logging.getLogger('destral.testing')


class OOTestCase(unittest.TestCase):
    """Base class to inherit test cases from for OpenERP Testing Framework.
    """

    def setUp(self):
        self.openerp = OpenERPService()
        self.database = self.openerp.create_database()
        self.config = config_from_environment('OOTEST', ['module'])
        self.openerp.install_module(self.config['module'])

    def test_all_views(self):
        logger.info('Testing views for module %s', self.config['module'])
        imd_obj = self.openerp.pool.get('ir.model.data')
        view_obj = self.openerp.pool.get('ir.ui.view')
        with Transaction().start(self.database) as txn:
            view_ids = imd_obj.search(txn.cursor, txn.user, [
                ('model', '=', 'ir.ui.view'),
                ('module', '=', self.config['module'])
            ])
            if view_ids:
                for view in view_obj.browse(txn.cursor, txn.user, view_ids):
                    model = self.openerp.pool.get(view.model)
                    if model is None:
                        # Check if model exists
                        raise Exception(
                            'View (id: %s) references model %s which does not '
                            'exist' % (view.id, view.model)
                        )
                    logger.info('Testing view %s (id: %s)', view.name, view.id)
                    model.fields_view_get(txn.cursor, txn.uid, view.id,
                                          view.type)

    def tearDown(self):
        self.openerp.drop_database()
