# -*- coding: utf-8 -*-

import time
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

# class delivery_carrier(osv.osv):
#     _inherit = "delivery.carrier"
#     _columns = {
#         'use_webservice_pricelist': fields.boolean('Advanced Pricing by WebService', help="Check this box if ..."),
#         'webservice_id': fields.many2one('delivery.webservice', 'Service', 'WebService'),
#         'webservice_type': fields.char('Service Type', size=32),
#  }

class DeliveryGrid(osv.osv):
    _inherit = "delivery.grid"
#    _description = "Delivery Webservice"
    _columns = {
        'service': fields.char('Service Name', size=32),
        'service_type': fields.char('Name', size=32),
        'login': fields.char('Login:', size=32),
        'password': fields.char('Password:',size=32)
    }

