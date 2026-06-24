import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate database with demo data'

    def add_arguments(self, parser):
        parser.add_argument('--brokerages', type=int, default=2)
        parser.add_argument('--flush', action='store_true')
        parser.add_argument('--seed', type=int, default=42)
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        if not settings.DEBUG and not options['force']:
            self.stderr.write('ERROR: Aborting. Use --force to run with DEBUG=False.')
            return

        if options['flush']:
            self._flush()

        self.stdout.write('Installing Faker...')
        try:
            from faker import Faker
        except ImportError:
            self.stderr.write('Faker not installed. Run: pip install faker')
            return

        fake = Faker('pt_BR')
        Faker.seed(options['seed'])
        random.seed(options['seed'])

        n = options['brokerages']
        self.stdout.write(f'Creating {n} brokerages...')

        from tenants.models import Brokerage, Plan, Subscription
        from accounts.models import User
        from clients.models import Client
        from insurers.models import Insurer, LineOfBusiness
        from insurance.models import Proposal, Policy, CoveredItem, Renewal
        from claims.models import Claim
        from partners.models import Agent, Producer
        from commissions.models import Commission, CommissionSplit
        from crm.models import Pipeline, Stage, Deal
        from notifications.models import Notification

        plan = Plan.objects.first()
        if not plan:
            plan = Plan.objects.create(name='Free', slug='free', price='0.00', max_users=3, max_clients=100, max_policies=50)

        today = date.today()

        for i in range(n):
            with transaction.atomic():
                brokerage = Brokerage.objects.create(
                    legal_name=f'Corretora {fake.company()}',
                    trade_name=fake.company_suffix(),
                    cnpj=fake.cnpj(),
                    plan=plan,
                    owner=None,
                )

                owner = User.objects.create_user(
                    email=f'owner{i+1}@demo.com',
                    password='demo1234',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    brokerage=brokerage,
                    role='owner',
                )
                brokerage.owner = owner
                brokerage.save(update_fields=['owner'])

                Subscription.objects.create(brokerage=brokerage, plan=plan, status='active')

                # Users
                for role in ['manager', 'broker', 'agent', 'producer', 'operational']:
                    User.objects.create_user(
                        email=f'{role}{i+1}@demo.com',
                        password='demo1234',
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        brokerage=brokerage,
                        role=role,
                    )

                # Insurers
                insurers = []
                for _ in range(5):
                    ins = Insurer.objects.create(
                        brokerage=brokerage,
                        name=fake.company(),
                        cnpj=fake.cnpj(),
                        is_active=True,
                    )
                    insurers.append(ins)

                # LOBs (from signal)
                lobs = list(LineOfBusiness.objects.filter(brokerage=brokerage))

                # Agents & Producers
                agents = []
                for _ in range(3):
                    agent = Agent.objects.create(
                        brokerage=brokerage,
                        entity_type=random.choice(['person', 'company']),
                        name=fake.name(),
                        document=fake.cpf(),
                        email=fake.email(),
                        phone=fake.phone_number(),
                        default_commission_rate=Decimal(str(random.uniform(5, 20))),
                        is_active=True,
                    )
                    agents.append(agent)

                producers = []
                for j in range(5):
                    producer = Producer.objects.create(
                        brokerage=brokerage,
                        agent=random.choice(agents) if j < 3 else None,
                        entity_type='person',
                        name=fake.name(),
                        document=fake.cpf(),
                        email=fake.email(),
                        default_commission_rate=Decimal(str(random.uniform(3, 15))),
                        is_active=True,
                    )
                    producers.append(producer)

                # Clients
                clients = []
                for _ in range(15):
                    pt = random.choice(['PF', 'PJ'])
                    client = Client.objects.create(
                        brokerage=brokerage,
                        person_type=pt,
                        name=fake.name() if pt == 'PF' else fake.company(),
                        document=fake.cpf() if pt == 'PF' else fake.cnpj(),
                        email=fake.email(),
                        phone=fake.phone_number(),
                        birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80) if pt == 'PF' else None,
                        is_active=True,
                    )
                    clients.append(client)

                # Proposals & Policies
                statuses_p = ['draft', 'sent', 'under_analysis', 'approved', 'rejected', 'converted']
                statuses_pol = ['active', 'expired', 'canceled', 'renewed']

                for j in range(10):
                    client = random.choice(clients)
                    insurer = random.choice(insurers)
                    lob = random.choice(lobs) if lobs else None
                    producer = random.choice(producers) if producers else None

                    start = today - timedelta(days=random.randint(0, 365))
                    end = start + timedelta(days=365)
                    premium = Decimal(str(random.uniform(500, 5000)))

                    proposal = Proposal.objects.create(
                        brokerage=brokerage,
                        client=client,
                        insurer=insurer,
                        line_of_business=lob,
                        producer=producer,
                        number=f'PROP-{i+1}-{j+1:04d}',
                        status=random.choice(statuses_p),
                        net_premium=premium,
                        total_premium=premium * Decimal('1.1'),
                        iof=premium * Decimal('0.1'),
                        proposed_start_date=start,
                        proposed_end_date=end,
                    )

                    # Covered items
                    for _ in range(random.randint(1, 3)):
                        CoveredItem.objects.create(
                            brokerage=brokerage,
                            proposal=proposal,
                            item_type=random.choice(['auto', 'property', 'life', 'other']),
                            description=f'{fake.word()} - {fake.word()}',
                            identifier=fake.license_plate() if random.random() > 0.5 else '',
                            insured_amount=Decimal(str(random.uniform(10000, 200000))),
                        )

                    if random.random() > 0.4:
                        pol_start = today - timedelta(days=random.randint(0, 300))
                        pol_end = pol_start + timedelta(days=365)
                        policy = Policy.objects.create(
                            brokerage=brokerage,
                            proposal=proposal,
                            policy_number=f'POL-{i+1}-{j+1:04d}',
                            client=client,
                            insurer=insurer,
                            line_of_business=lob,
                            producer=producer,
                            status=random.choice(statuses_pol),
                            net_premium=premium,
                            total_premium=premium * Decimal('1.1'),
                            iof=premium * Decimal('0.1'),
                            commission_rate=Decimal(str(random.uniform(10, 25))),
                            start_date=pol_start,
                            end_date=pol_end,
                        )

                        # Commission
                        comm_amount = premium * policy.commission_rate / Decimal('100')
                        Commission.objects.create(
                            brokerage=brokerage,
                            policy=policy,
                            base_premium=premium,
                            insurer_rate=policy.commission_rate,
                            insurer_amount=comm_amount,
                            status=random.choice(['pending', 'received', 'paid']),
                            reference_date=pol_start,
                        )

                # Claims
                for j in range(3):
                    policy = Policy.objects.filter(brokerage=brokerage).first()
                    if policy:
                        items = list(policy.covered_items.all())
                        if items:
                            Claim.objects.create(
                                brokerage=brokerage,
                                policy=policy,
                                covered_item=random.choice(items),
                                claim_number=f'SIN-{i+1}-{j+1:03d}',
                                occurrence_date=today - timedelta(days=random.randint(1, 180)),
                                notice_date=today - timedelta(days=random.randint(0, 30)),
                                status=random.choice(['opened', 'under_analysis', 'approved', 'denied', 'paid', 'closed']),
                                claimed_amount=Decimal(str(random.uniform(1000, 50000))),
                            )

                # CRM
                pipeline = Pipeline.objects.filter(brokerage=brokerage, is_default=True).first()
                if pipeline:
                    stages = list(pipeline.stages.all())
                    for j in range(8):
                        stage = random.choice(stages) if stages else None
                        deal = Deal.objects.create(
                            brokerage=brokerage,
                            pipeline=pipeline,
                            stage=stage,
                            client=random.choice(clients),
                            producer=random.choice([p.user for p in producers if p.user] or [owner]),
                            title=f'{fake.job()} - {fake.company()}',
                            estimated_value=Decimal(str(random.uniform(1000, 50000))),
                            status='won' if stage and stage.is_won else ('lost' if stage and stage.is_lost else 'open'),
                            expected_close_date=today + timedelta(days=random.randint(-30, 90)),
                        )

                self.stdout.write(f'  Brokerage {i+1}: {brokerage.legal_name} — DONE')

        self.stdout.write(self.style.SUCCESS(f'Seed complete! Created {n} brokerages with demo data.'))
        self.stdout.write(f'Login: owner1@demo.com / demo1234')

    def _flush(self):
        self.stdout.write('Flushing demo data...')
        from tenants.models import Brokerage
        Brokerage.objects.all().delete()
        self.stdout.write('Flush complete.')
