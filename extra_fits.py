
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
#
#
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german_442@hotmail.com)
#
##############################################################################

from osv import osv, fields
from openerp import SUPERUSER_ID

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    def _get_total_vol(self, cr, uid, ids, field_name, arg, context=None):
        result={}
        cost_total = 0.0
        for rec in self.browse(cr, uid, ids, context=None):
            for line in rec.move_ids:
                cost_total += line.cost_total
            result[rec.id] = cost_total
        return result

    _columns = {
        'cost_total': fields.function(_get_total_vol, string="Costo Total", method=True, type='float', digits=(18,2), store=True, readonly=True),
        }
stock_inventory()

class stock_move(osv.osv):
    _inherit = "stock.move"
    def _get_total_vol(self, cr, uid, ids, field_name, arg, context=None):
        result={}
        cost_total = 0.0
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.product_id.standard_price and rec.product_qty > 0 :
                cost_total = rec.product_id.standard_price * rec.product_qty
            result[rec.id] = cost_total
        return result

    _columns = {
        'cost_total': fields.function(_get_total_vol, string="Costo", method=True, type='float', digits=(18,2), store=True, readonly=True),
        }
stock_move()

class report_inventory_cegasa(osv.osv):
    _name = 'report.inventory.cegasa'
    _description = 'Reporte de Inventario Fisico para Cegasa'
    _columns = {
        'name':fields.char('Nombre', size=64, required=False, readonly=False), 
    }
    _defaults = {  
        }
    def init(self, cr,):
        report_obj = self.pool.get('ir.actions.report.xml')
        report_picking_id = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','stock/report/stock_inventory_move.rml')])
        report_obj.write(cr, SUPERUSER_ID, report_picking_id, {'report_file':'ps_stock_inventory/report/stock_inventory_move.rml'})
        return True
report_inventory_cegasa()

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit ='stock.picking'
    
    def _get_si_timbre_no(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        timbrado_c_cfdi = False
        for rec in self.browse(cr,uid,ids,context=context):
            ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
            attach_facturae_id = ir_attach_obj.search(cr, SUPERUSER_ID,
                [('model_source','=','account.invoice'),
                ('id_source','=',ids[0])])
            if attach_facturae_id:
                for attachm_mx in ir_attach_obj.browse(cr, uid, attach_facturae_id, context):
                    if attachm_mx.state not in ('draft','confirmed','cancel'):
                        timbrado_c_cfdi = True
            res[rec.id] = timbrado_c_cfdi
        return res

    _columns = {
        'location_id_cg': fields.char("Ubicacion Origen", size=256),
        'location_dest_id_cg': fields.char("Ubicacion Destino", size=256),
        }

    _defaults = {
        }

    def create(self, cr, uid, vals, context=None):
        res = super(stock_picking, self).create(
            cr, uid, vals, context)
        cr.execute("""
            select name from stock_location where id in
                (select location_id from stock_move where picking_id=%s)
                group by name;
            """,(res,))
        cr_res = cr.fetchall()
        if cr_res:
            origen = [str(x[0]) for x in cr_res]
            if origen:
                origen = str(origen).replace("[","").replace("]","").replace("'","")
                cr.execute("""
                    update stock_picking set location_id_cg=%s
                        where id=%s;
                    """,(origen,res,))
        cr.execute("""
            select name from stock_location where id in
                (select location_dest_id from stock_move where picking_id=%s)
                group by name;
            """,(res,))
        cr_res = cr.fetchall()

        if cr_res:
            destino = [str(x[0]) for x in cr_res]
            if destino:
                destino = str(destino).replace("[","").replace("]","").replace("'","")
                cr.execute("""
                    update stock_picking set location_dest_id_cg=%s
                        where id=%s;
                    """,(destino,res,))
        return res