# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2014  Luis Felipe Mileo - KMEE - www.kmee.com.br              #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

import time
from openerp.osv import orm, osv
from openerp.tools.translate import _

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def delivery_set(self, cr, uid, ids, context=None):
        #Copia do modulo delivery
        #Exceto pelo final que adiciona ao campo total do frete.
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')

        for order in self.browse(cr, uid, ids, context=context):
            term = 0
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id],
            order.partner_shipping_id.id)

            if not grid_id:
                raise osv.except_osv(_('No Grid Available!'),
                     _('No grid matching for this carrier!'))

            if not order.state in ('draft'):
                raise osv.except_osv(_('Order not in Draft State!'),
                    _('The order state have to be draft to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)
            if (grid.service == "correios"):
                amount_freight,term = grid_obj.get_price_term(cr, uid, grid, order, context)
            else:
                amount_freight = grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context)
            note = ""
            if term > 0:
                note = "Prazo de entrega {0} dia(s)".format(term)
            super(SaleOrder, self).onchange_amount_freight(cr, uid, ids, amount_freight)
        return self.write(cr, uid, ids, {'amount_freight': amount_freight, 'note': note})