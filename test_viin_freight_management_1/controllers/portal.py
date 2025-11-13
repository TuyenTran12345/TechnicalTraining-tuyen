from collections import OrderedDict
from datetime import timedelta

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.fields import Datetime


class FreightPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Add shipment counter to portal home page"""
        values = super()._prepare_home_portal_values(counters)

        if 'shipment_count' in counters:
            values['shipment_count'] = request.env['freight.shipment'].search_count([])

        return values

    def _prepare_shipment_domain(self):
        """Return the domain for shipments the current user can access"""
        return []

    def _shipment_get_searchbar_filters(self):
        """Return customer-oriented filters for shipments"""
        return OrderedDict([
            ('all', {'label': _('All Shipments'), 'domain': []}),

            ('active', {'label': _('Active Shipments'), 'domain': [('last_tracking_status', 'in', ['on_track', 'at_risk'])]}),
            ('on_track', {'label': _('On Track'), 'domain': [('last_tracking_status', '=', 'on_track')]}),
            ('attention', {'label': _('Need Attention'), 'domain': [('last_tracking_status', 'in', ['at_risk', 'off_track', 'on_hold'])]}),
            ('completed', {'label': _('Completed'), 'domain': [('is_closed', '=', True)]}),

            # Transport mode filters - customers often search by how they ship
            ('sea_freight', {'label': _('Sea Freight'), 'domain': [('transport_mode', '=', 'sea')]}),
            ('air_freight', {'label': _('Air Freight'), 'domain': [('transport_mode', '=', 'air')]}),
            ('land_transport', {'label': _('Land Transport'), 'domain': [('transport_mode', '=', 'land')]}),

            # Direction filters - very important for customers
            ('import', {'label': _('Import'), 'domain': [('direction', '=', 'import')]}),
            ('export', {'label': _('Export'), 'domain': [('direction', '=', 'export')]}),
            ('domestic', {'label': _('Domestic'), 'domain': [('direction', '=', 'domestic')]}),

            # Time-based filters - customers frequently look for recent shipments
            ('recent', {'label': _('Last 30 Days'), 'domain': [('create_date', '>=', (Datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))]}),
            ('this_month', {'label': _('This Month'), 'domain': [('create_date', '>=', Datetime.now().replace(day=1).strftime('%Y-%m-%d'))]}),
        ])

    def _shipment_get_search_domain(self, search_in, search):
        """Build search domain based on search input and search term"""
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('hbl', 'all'):
            search_domain.append([('house_bill_number', 'ilike', search)])
        if search_in in ('mbl', 'all'):
            search_domain.append([('master_bill_number', 'ilike', search)])
        if search_in in ('customer', 'all'):
            search_domain.append([('customer_id.name', 'ilike', search)])
        if search_in in ('origin', 'all'):
            search_domain.append([('origin_id.name', 'ilike', search)])
        if search_in in ('destination', 'all'):
            search_domain.append([('destination_id.name', 'ilike', search)])
        return OR(search_domain)

    def _shipment_get_searchbar_sortings(self):
        """Return available sorting options for shipments"""
        return {
            'date': {'label': _('Date'), 'order': 'create_date desc'},
            'date_asc': {'label': _('Date (Oldest)'), 'order': 'create_date asc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'name_desc': {'label': _('Name (Z-A)'), 'order': 'name desc'},
            'stage': {'label': _('Stage'), 'order': 'current_stage_id'},
            'customer': {'label': _('Customer'), 'order': 'customer_id'},
            'customer_desc': {'label': _('Customer (Z-A)'), 'order': 'customer_id desc'},
        }

    def _shipment_get_searchbar_inputs(self):
        values = {
            'name': {'input': 'name', 'label': _('Search in Name'), 'order': 1},
            'hbl': {'input': 'hbl', 'label': _('Search in HBL'), 'order': 2},
            'mbl': {'input': 'mbl', 'label': _('Search in MBL'), 'order': 3},
            'customer': {'input': 'customer', 'label': _('Search in Customer'), 'order': 4},
            'origin': {'input': 'origin', 'label': _('Search in Origin'), 'order': 5},
            'destination': {'input': 'destination', 'label': _('Search in Destination'), 'order': 6},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]['order']))

    @http.route(['/my/shipments', '/my/shipments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shipments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='name', **kw):
        """Display the shipments list page"""
        values = self._prepare_portal_layout_values()
        FreightShipment = request.env['freight.shipment']

        domain = self._prepare_shipment_domain()

        searchbar_sortings = self._shipment_get_searchbar_sortings()
        searchbar_inputs = self._shipment_get_searchbar_inputs()
        searchbar_filters = self._shipment_get_searchbar_filters()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # default filterby
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search functionality
        if search and search_in:
            domain += self._shipment_get_search_domain(search_in, search)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        shipment_count = FreightShipment.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/shipments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=shipment_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        shipments = FreightShipment.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_shipments_history'] = shipments.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'shipments': shipments.sudo(),
            'page_name': 'shipment',
            'pager': pager,
            'default_url': '/my/shipments',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': searchbar_filters,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("viin_freight_management.portal_my_shipments", values)

    @http.route(['/my/shipment/<int:shipment_id>'], type='http', auth="user", website=True)
    def portal_my_shipment(self, shipment_id=None, **kw):
        """Display a single shipment"""
        try:
            shipment_sudo = self._document_check_access('freight.shipment', shipment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._prepare_shipment_page_values(shipment_sudo, **kw)
        return request.render("viin_freight_management.portal_my_shipment", values)

    def _prepare_shipment_page_values(self, shipment, **kwargs):
        """Prepare values for rendering the shipment page"""
        values = {
            'page_name': 'shipment',
            'shipment': shipment,
        }

        # Get tracking history (published only)
        values['tracking_history'] = shipment.shipment_tracking_ids.filtered(lambda t: t.is_published)

        return self._get_page_view_values(
            shipment,
            access_token=kwargs.get('access_token', False),
            values=values,
            view_type='form',
            session_history='my_shipments_history',
            no_breadcrumbs=False,
            **kwargs
        )
