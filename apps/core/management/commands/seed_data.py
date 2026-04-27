"""
Management command: seed_data
Seeds the database with the initial data from 002_seed_data.sql.
Adapted for the consolidated schema (11 tables).

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush    # clears existing data first
"""
import logging
from datetime import date, timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed the database with initial Popna Entertainment data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before seeding.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        with transaction.atomic():
            org = self._create_organization()
            self._create_users(org)
            self._create_inventory(org)
            self._create_contacts(org)
            self._create_settings(org)
            self._create_complaints(org)
            self._create_connection_requests(org)
            self._create_invoices(org)

        self.stdout.write(self.style.SUCCESS('Seed data loaded successfully.'))

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush(self):
        from apps.users.models import Organization
        self.stdout.write('Flushing existing data …')
        Organization.objects.filter(id='org_001').delete()
        self.stdout.write(self.style.WARNING('Existing seed data deleted.'))

    # ------------------------------------------------------------------
    # Organization
    # ------------------------------------------------------------------

    def _create_organization(self):
        from apps.users.models import Organization
        org, created = Organization.objects.get_or_create(
            id='org_001',
            defaults={
                'name': 'Popna Entertainment',
                'status': 'active',
                'allowed_modules': [
                    'dashboard', 'contacts', 'complaints', 'payments',
                    'invoices', 'purchase-invoices', 'users', 'settings',
                    'connection-requests', 'inventory-products', 'products',
                    'branches', 'pos',
                ],
                'allowed_settings_tabs': ['company', 'products', 'billing', 'pos'],
                'industry_type': 'isp',
                'terminology': {},
                'subscription_start': date(2025, 1, 1),
                'subscription_end': date(2027, 12, 31),
            },
        )
        action = 'Created' if created else 'Already exists'
        self.stdout.write(f'  Organization: {action} — {org.name}')
        return org

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _create_users(self, org):
        from apps.users.models import User

        users_data = [
            {
                'organization': org,
                'name': 'Admin User',
                'username': 'bankaitech',
                'password': make_password('test123'),
                'role': 'admin',
                'status': 'active',
                'allowed_modules': [],
                'branch_id': 1,
            },
            {
                'organization': org,
                'name': 'Employee User',
                'username': 'bankaitech-emp',
                'password': make_password('test123'),
                'role': 'employee',
                'status': 'active',
                'allowed_modules': ['contacts', 'complaints'],
                'branch_id': 1,
            },
        ]

        # Super admin
        User.objects.get_or_create(
            username='superadmin',
            organization=None,
            defaults={
                'name': 'Super Admin',
                'password': make_password('superadmin123'),
                'role': 'super_admin',
                'status': 'active',
                'allowed_modules': [],
            },
        )
        self.stdout.write('  Super admin: bankaitech / superadmin123')

        for data in users_data:
            User.objects.get_or_create(
                username=data['username'],
                organization=org,
                defaults=data,
            )

        self.stdout.write('  Users: bankaitech (admin), bankaitech-emp (employee) — password: test123')

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def _create_inventory(self, org):
        from apps.inventory.models import Inventory

        categories = [
            {
                'catalog_type': 'isp_category',
                'name': 'Cable',
                'price': 0,
                'is_active': True,
                'meta': {'isp_type': 'cable', 'cutoff_date': 10, 'cutoff_days': None},
            },
            {
                'catalog_type': 'isp_category',
                'name': 'Internet 1',
                'price': 0,
                'is_active': True,
                'meta': {'isp_type': 'internet', 'cutoff_date': None, 'cutoff_days': 7},
            },
            {
                'catalog_type': 'isp_category',
                'name': 'Internet 2',
                'price': 0,
                'is_active': True,
                'meta': {'isp_type': 'internet', 'cutoff_date': None, 'cutoff_days': 7},
            },
            {
                'catalog_type': 'isp_category',
                'name': 'Internet 3',
                'price': 0,
                'is_active': True,
                'meta': {'isp_type': 'internet', 'cutoff_date': None, 'cutoff_days': 15},
            },
        ]

        plans = [
            # Cable
            ('Cable', 'Cable Basic 50 Mbps', 499, 18, 500, 'High-speed cable broadband with 50 Mbps.'),
            ('Cable', 'Cable Premium 100 Mbps', 799, 18, 500, 'Premium cable broadband with 100 Mbps.'),
            ('Cable', 'Cable Ultra 200 Mbps', 1299, 18, 1000, 'Ultra-fast cable broadband with 200 Mbps.'),
            # Internet 1
            ('Internet 1', 'Internet 1 Fiber Basic', 449, 18, 500, 'Reliable fiber connection.'),
            ('Internet 1', 'Internet 1 Fiber Plus', 699, 18, 500, 'Enhanced fiber connection.'),
            ('Internet 1', 'Internet 1 Fiber Premium', 999, 18, 1000, 'Premium fiber connection.'),
            # Internet 2
            ('Internet 2', 'Internet 2 Express 75 Mbps', 599, 18, 500, 'Fast and reliable 75 Mbps.'),
            ('Internet 2', 'Internet 2 Speed 150 Mbps', 899, 18, 500, '150 Mbps for power users.'),
            ('Internet 2', 'Internet 2 Turbo 300 Mbps', 1499, 18, 1000, 'Blazing fast 300 Mbps.'),
            # Internet 3
            ('Internet 3', 'Internet 3 Rural Connect', 399, 18, 500, 'Rural area connectivity.'),
            ('Internet 3', 'Internet 3 Home Plus', 549, 18, 500, 'Enhanced home internet.'),
            ('Internet 3', 'Internet 3 Business', 799, 18, 1000, 'Business-grade internet.'),
        ]

        # Physical product
        products = [
            {
                'catalog_type': 'product',
                'name': 'Dual-Band WiFi Router',
                'sku': 'ROUTER-001',
                'price': 1200,
                'purchase_price': 900,
                'current_stock': 25,
                'stock_alert': 5,
                'is_active': True,
                'meta': {},
            },
            {
                'catalog_type': 'product',
                'name': 'Network Switch 8-Port',
                'sku': 'SWITCH-008',
                'price': 800,
                'purchase_price': 600,
                'current_stock': 10,
                'stock_alert': 3,
                'is_active': True,
                'meta': {},
            },
        ]

        for cat_data in categories:
            Inventory.objects.get_or_create(
                organization=org,
                catalog_type=cat_data['catalog_type'],
                name=cat_data['name'],
                defaults={**cat_data},
            )

        for provider, name, price, gst_rate, install, desc in plans:
            Inventory.objects.get_or_create(
                organization=org,
                catalog_type='isp_plan',
                name=name,
                defaults={
                    'price': price,
                    'description': desc,
                    'is_active': True,
                    'meta': {
                        'provider': provider,
                        'gst_rate': gst_rate,
                        'installation_amount': install,
                        'permanent_discount': 0,
                    },
                },
            )

        for prod_data in products:
            Inventory.objects.get_or_create(
                organization=org,
                sku=prod_data['sku'],
                defaults={**prod_data},
            )

        self.stdout.write('  Inventory: 4 ISP categories, 12 plans, 2 products')

    # ------------------------------------------------------------------
    # Contacts (customers + suppliers + vendors)
    # ------------------------------------------------------------------

    def _create_contacts(self, org):
        from apps.contacts.models import Contact

        now = timezone.now()

        customers = [
            ('Rajesh Kumar', 'rajesh.kumar@example.com', '9876543210', 'Cable', 'Cable Basic 50 Mbps',
             'Active', 'paid', 'upi', 589, 0, 'BOX-001', 'STB-MH-001', 'Andheri West', 1, 45),
            ('Priya Sharma', 'priya.sharma@example.com', '9876543211', 'Internet 1', 'Internet 1 Fiber Basic',
             'Active', 'not_paid', None, 0, 0, None, None, 'Connaught Place', 1, 25),
            ('Amit Patel', 'amit.patel@example.com', '9876543212', 'Internet 2', 'Internet 2 Express 75 Mbps',
             'Inactive', 'not_paid', None, 0, 707, None, None, 'Koramangala', 1, 60),
            ('Sneha Reddy', 'sneha.reddy@example.com', '9876543213', 'Cable', 'Cable Premium 100 Mbps',
             'Inactive', 'not_paid', None, 0, 943, 'BOX-004', 'STB-TS-004', 'Banjara Hills', 1, 15),
            ('Vikram Singh', 'vikram.singh@example.com', '9876543214', 'Internet 3', 'Internet 3 Rural Connect',
             'Active', 'paid', 'cash', 471, 0, None, None, 'Wakad', 1, 5),
            ('Anjali Mehta', 'anjali.mehta@example.com', '9876543215', 'Internet 1', 'Internet 1 Fiber Plus',
             'Active', 'paid', 'upi', 825, 0, None, None, 'T. Nagar', 1, 30),
            ('Rahul Verma', 'rahul.verma@example.com', '9876543216', 'Internet 2', 'Internet 2 Speed 150 Mbps',
             'Active', 'paid', 'card', 1061, 0, None, None, 'DLF Cyber City', 1, 8),
            ('Kavita Nair', 'kavita.nair@example.com', '9876543217', 'Cable', 'Cable Ultra 200 Mbps',
             'Active', 'paid', 'cash', 1533, 0, 'BOX-008', 'STB-UP-008', 'Sector 62', 2, 12),
            ('Mohit Agarwal', 'mohit.agarwal@example.com', '9876543218', 'Internet 1', 'Internet 1 Fiber Premium',
             'Inactive', 'not_paid', None, 0, 0, None, None, None, 2, 90),
            ('Divya Joshi', 'divya.joshi@example.com', '9876543219', 'Internet 3', 'Internet 3 Home Plus',
             'Active', 'not_paid', None, 0, 0, None, None, None, 2, 20),
            ('Arjun Malhotra', 'arjun.malhotra@example.com', '9876543220', 'Internet 2', 'Internet 2 Turbo 300 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 2, 3),
            ('Pooja Desai', 'pooja.desai@example.com', '9876543221', 'Cable', 'Cable Basic 50 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 2, 18),
            ('Suresh Iyer', 'suresh.iyer@example.com', '9876543222', 'Internet 1', 'Internet 1 Fiber Basic',
             'Inactive', 'not_paid', None, 0, 0, None, None, None, 2, 75),
            ('Meera Krishnan', 'meera.krishnan@example.com', '9876543223', 'Internet 3', 'Internet 3 Business',
             'Active', 'not_paid', None, 0, 0, None, None, None, 3, 10),
            ('Nikhil Kapoor', 'nikhil.kapoor@example.com', '9876543224', 'Cable', 'Cable Premium 100 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 3, 7),
            ('Riya Banerjee', 'riya.banerjee@example.com', '9876543225', 'Internet 2', 'Internet 2 Express 75 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 3, 22),
            ('Karan Thakur', 'karan.thakur@example.com', '9876543226', 'Internet 1', 'Internet 1 Fiber Plus',
             'Active', 'not_paid', None, 0, 0, None, None, None, 3, 14),
            ('Shreya Menon', 'shreya.menon@example.com', '9876543227', 'Internet 3', 'Internet 3 Rural Connect',
             'Inactive', 'not_paid', None, 0, 0, None, None, None, 3, 50),
            ('Aditya Rao', 'aditya.rao@example.com', '9876543228', 'Cable', 'Cable Ultra 200 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 3, 2),
            ('Neha Gupta', 'neha.gupta@example.com', '9876543229', 'Internet 2', 'Internet 2 Speed 150 Mbps',
             'Active', 'not_paid', None, 0, 0, None, None, None, 1, 1),
            ('Rohit Sharma', 'rohit.sharma@example.com', '9876543230', 'Internet 1', 'Internet 1 Fiber Premium',
             'Active', 'not_paid', None, 0, 0, None, None, None, 1, 6),
            ('Sonal Bhatt', 'sonal.bhatt@example.com', '9876543231', 'Internet 3', 'Internet 3 Business',
             'Active', 'not_paid', None, 0, 0, None, None, None, 1, 9),
        ]

        for (name, email, mobile, conn_type, package, status, pay_status,
             pay_method, collected, balance, box_no, stb_no, area, branch_id, days_ago) in customers:
            Contact.objects.get_or_create(
                organization=org,
                contact_type='customer',
                mobile=mobile,
                defaults={
                    'name': name,
                    'email': email,
                    'connection_type': conn_type,
                    'package': package,
                    'status': status,
                    'payment_status': pay_status,
                    'payment_method': pay_method,
                    'collected_amount': collected,
                    'balance_amount': balance,
                    'box_number': box_no,
                    'stb_number': stb_no,
                    'area': area,
                    'branch_id': branch_id,
                    'country': 'India',
                },
            )

        # Suppliers
        suppliers = [
            ('Network Supplies Co.', 'info@networksupplies.com', '9000001111', 'Vikash Jain', 1),
            ('Tech Hardware Hub', 'sales@techhardware.com', '9000002222', 'Meena Kapoor', 1),
        ]
        for name, email, mobile, cp, branch_id in suppliers:
            Contact.objects.get_or_create(
                organization=org,
                contact_type='supplier',
                mobile=mobile,
                defaults={
                    'name': name,
                    'email': email,
                    'contact_person': cp,
                    'branch_id': branch_id,
                    'country': 'India',
                },
            )

        # Vendors
        vendors = [
            ('CloudHost Vendor', 'vendor@cloudhost.com', '9000003333', 'Ashok Mehta', 1),
            ('Infra Solutions Ltd', 'sales@infrasol.com', '9000004444', 'Priya Nair', 2),
        ]
        for name, email, mobile, cp, branch_id in vendors:
            Contact.objects.get_or_create(
                organization=org,
                contact_type='vendor',
                mobile=mobile,
                defaults={
                    'name': name,
                    'email': email,
                    'contact_person': cp,
                    'branch_id': branch_id,
                    'country': 'India',
                },
            )

        self.stdout.write('  Contacts: 22 customers, 2 suppliers, 2 vendors')

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _create_settings(self, org):
        from apps.org_settings.models import OrgSettings
        OrgSettings.objects.get_or_create(
            organization=org,
            defaults={
                'company_name': 'Popna Entertainment',
                'gstin': '27AABCU9603R1ZM',
                'address_line1': '101 Business Park',
                'address_line2': 'Andheri East',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'pincode': '400069',
                'contact_number': '9000000000',
                'email': 'admin@popnaentertainment.com',
                'branches': [
                    {
                        'id': 1,
                        'name': 'Main Office',
                        'location': 'Mumbai Central',
                        'address': '101 Business Park, Mumbai',
                        'phone': '9000000000',
                        'gstin': '27AABCU9603R1ZM',
                        'is_active': True,
                    },
                    {
                        'id': 2,
                        'name': 'North Branch',
                        'location': 'Andheri',
                        'address': '45 Link Road, Andheri West',
                        'phone': '9000000011',
                        'is_active': True,
                    },
                    {
                        'id': 3,
                        'name': 'South Branch',
                        'location': 'Thane',
                        'address': '7 Station Road, Thane',
                        'phone': '9000000022',
                        'is_active': True,
                    },
                ],
                'sms_enabled': False,
                'upi_id': 'popnaentertainment@upi',
                'upi_display_name': 'Popna Entertainment',
                'upi_enabled': True,
                'upi_supported_apps': ['gpay', 'phonepe', 'paytm', 'bhim'],
                'website': {
                    'heroTitle': 'Fast & Reliable Internet',
                    'heroSubtitle': 'Connecting Communities',
                    'heroDescription': 'Experience blazing-fast internet with Popna Entertainment.',
                    'ctaButtonText': 'Get Connected',
                    'ctaButtonLink': '/contact',
                },
            },
        )
        self.stdout.write('  Settings: company profile, 3 branches, UPI config')

    # ------------------------------------------------------------------
    # Complaints (Activities)
    # ------------------------------------------------------------------

    def _create_complaints(self, org):
        from apps.activities.models import Activity
        from apps.contacts.models import Contact

        contacts = list(
            Contact.objects.filter(organization=org, contact_type='customer')[:5]
        )

        complaints = [
            ('No internet connectivity', 'open', 'high'),
            ('Slow speed issue', 'in_progress', 'medium'),
            ('Cable TV signal lost', 'resolved', 'low'),
            ('Billing discrepancy', 'open', 'medium'),
            ('Router not working', 'in_progress', 'high'),
        ]

        for i, (desc, status, priority) in enumerate(complaints):
            contact = contacts[i % len(contacts)] if contacts else None
            Activity.objects.get_or_create(
                organization=org,
                kind='complaint',
                contact=contact,
                defaults={
                    'status': status,
                    'priority': priority,
                    'payload': {
                        'customerName': contact.name if contact else '',
                        'mobile': contact.mobile if contact else '',
                        'customerDescription': desc,
                        'internalDescription': '',
                        'slaHours': 24,
                    },
                },
            )

        self.stdout.write('  Activities: 5 complaints seeded')

    # ------------------------------------------------------------------
    # Connection Requests
    # ------------------------------------------------------------------

    def _create_connection_requests(self, org):
        from apps.activities.models import Activity

        requests_data = [
            ('Aryan Bose', '9111222333', 'aryan@example.com', 'Cable Basic 50 Mbps'),
            ('Lata Verma', '9111222444', 'lata@example.com', 'Internet 1 Fiber Basic'),
            ('Sudhir Rao', '9111222555', 'sudhir@example.com', 'Internet 2 Express 75 Mbps'),
        ]

        for name, mobile, email, plan in requests_data:
            Activity.objects.get_or_create(
                organization=org,
                kind='connection_request',
                defaults={
                    'status': 'new',
                    'payload': {
                        'name': name,
                        'mobile': mobile,
                        'email': email,
                        'planName': plan,
                    },
                },
            )

        self.stdout.write('  Activities: 3 connection requests seeded')

    # ------------------------------------------------------------------
    # Invoices
    # ------------------------------------------------------------------

    def _create_invoices(self, org):
        from apps.invoices.models import Invoice
        from apps.contacts.models import Contact

        customers = list(
            Contact.objects.filter(organization=org, contact_type='customer')[:3]
        )

        today = date.today()

        invoices = [
            {
                'kind': 'sales',
                'invoice_number': 'INV-2024-001',
                'status': 'paid',
                'issue_date': today - timedelta(days=30),
                'contact': customers[0] if customers else None,
                'customer_name': customers[0].name if customers else 'Rajesh Kumar',
                'subtotal': 499,
                'tax_total': 89.82,
                'total_amount': 588.82,
                'items': [
                    {
                        'productId': None,
                        'productName': 'Cable Basic 50 Mbps',
                        'quantity': 1,
                        'unitPrice': 499,
                        'taxRate': 18,
                        'discount': 0,
                        'lineTotal': 588.82,
                    }
                ],
                'payload': {
                    'serviceProvider': 'Cable',
                    'planName': 'Cable Basic 50 Mbps',
                    'gstRate': 18,
                    'gstAmount': 89.82,
                    'invoiceType': 'tax_invoice',
                },
            },
            {
                'kind': 'purchase',
                'invoice_number': 'PINV-2024-001',
                'status': 'paid',
                'issue_date': today - timedelta(days=15),
                'vendor_name': 'Network Supplies Co.',
                'subtotal': 9000,
                'tax_total': 1620,
                'total_amount': 10620,
                'items': [
                    {
                        'productName': 'Dual-Band WiFi Router',
                        'quantity': 10,
                        'unitPrice': 900,
                        'taxRate': 18,
                        'discount': 0,
                        'lineTotal': 10620,
                    }
                ],
                'payload': {'reference': 'PO-001', 'cgst': 810, 'sgst': 810, 'igst': 0},
            },
            {
                'kind': 'pos',
                'invoice_number': 'POS-2024-001',
                'status': 'completed',
                'issue_date': today,
                'customer_name': 'Walk-in Customer',
                'subtotal': 1200,
                'tax_total': 216,
                'total_amount': 1416,
                'items': [
                    {
                        'productName': 'Dual-Band WiFi Router',
                        'quantity': 1,
                        'unitPrice': 1200,
                        'taxRate': 18,
                        'discount': 0,
                        'lineTotal': 1416,
                    }
                ],
                'payload': {'method': 'cash', 'notes': 'Walk-in sale'},
            },
        ]

        for inv_data in invoices:
            Invoice.objects.get_or_create(
                organization=org,
                invoice_number=inv_data['invoice_number'],
                defaults={**inv_data},
            )

        self.stdout.write('  Invoices: 1 sales, 1 purchase, 1 POS seeded')
