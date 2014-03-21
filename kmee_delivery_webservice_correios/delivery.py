# -*- coding: utf-8 -*-

import time
import math
from pycorreios import Correios
from openerp.osv import fields,osv
from openerp.tools.translate import _

class DeliveryCarrier(osv.osv):
    _inherit = "delivery.carrier"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        if context is None:
            context = {}
        order_id = context.get('order_id',False)
        if not order_id:
            res = super(DeliveryCarrier, self).name_get(cr, uid, ids, context=context)
        else:
            order = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
            currency = order.pricelist_id.currency_id.name or ''
            res = [(r['id'], r['name']+' ('+(str(r['price']))+' '+currency+' '+ str(r['term'])+' dia(s))') for r in self.read(cr, uid, ids, ['name', 'price', 'term'], context)]
        return res
        
    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        res={}
        if context is None:
            context = {}
        sale_obj=self.pool.get('sale.order')
        grid_obj=self.pool.get('delivery.grid')
        for carrier in self.browse(cr, uid, ids, context=context):
            order_id=context.get('order_id',False)
            res[carrier.id] = {
                'price': 0.00,
                'term': 0.00,
            }
            if order_id:
                order = sale_obj.browse(cr, uid, order_id, context=context)
                carrier_grid=self.grid_get(cr,uid,[carrier.id],order.partner_shipping_id.id,context)
                if carrier_grid:
                    grid = grid_obj.browse(cr, uid, carrier_grid, context=context)
                    print grid.service

                    if (grid.service == "correios"): #CHANGE
                        res[carrier.id]['price'],res[carrier.id]['term'] = grid_obj.get_price_term(cr, uid, grid, order, context)
                    else:
                        res[carrier.id]['price']=grid_obj.get_price(cr, uid, carrier_grid, order, time.strftime('%Y-%m-%d'), context)
        return res

    _columns = {
       'price' : fields.function(get_price, string='Price', multi="sums"),
       'term' : fields.function(get_price, string='Term', multi="sums"),
       }
    
class DeliveryGrid(osv.osv):
    _inherit = "delivery.grid"

    def get_price_term(self, cr, uid, grid, order, context):
        total = 0
        weight = 0
        volume = 0
        for line in order.order_line:
            if not line.product_id:
                continue
            total += line.price_subtotal or 0.0
            weight += (line.product_id.weight or 0.0) * line.product_uom_qty
            volume += (line.product_id.volume or 0.0) * line.product_uom_qty            

        volume_cm = volume * 100000
        peso_volumetrico = 0
        
        if (volume_cm > 60000):
            peso_volumetrico = math.ceil(volume_cm / 6000)
            
        peso_considerado = max(weight, peso_volumetrico)
        aresta = int(math.ceil(volume_cm**(1/3.0)))

        fields = {
                  "cod": int(grid.service_type),
                  "GOCEP": order.partner_shipping_id.zip,
                  "HERECEP": order.shop_id.company_id.partner_id.zip,
                  "peso": peso_considerado,
                  "formato": "1", # caixa/pacote
                  "comprimento": aresta,
                  "altura": aresta,
                  "largura": aresta,
                  "diametro": "0",
                  "empresa": grid.login,
                  "senha": grid.password,
                  }

        try:
            response = Correios().frete(**fields)
        except Exception:
            return (0.00, 0.00)
            # raise osv.except_osv(_('Erro no calculo do frete!'),
            #                      _('Nao foi possivel conectar'))
        return (float(response['Valor'].replace(",", ".")),response['PrazoEntrega'] or 0.00)