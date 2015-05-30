"""
Creates test data
"""
from ozpcenter import models as models

def create_sample_data():
	"""
	Creates basic sample data
	"""
	# Categories
	cat = models.Category(title="Books and Reference",
		description="Things made of paper")
	cat.save()
	cat = models.Category(title="Business",
		description="For making money")
	cat.save()
	cat = models.Category(title="Education",
		description="Educational in nature")
	cat.save()
	cat = models.Category(title="Entertainment",
		description="For fun")
	cat.save()
	cat = models.Category(title="Tools",
		description="Tools and Utilities")
	cat.save()


	# Contact Types
	p = modles.ContactType(name='Worker')
	p.save()
	p = modles.ContactType(name='Manager')
	p.save()
	p = modles.ContactType(name='Boss')
	p.save()

	# Listing Types
	t = models.ListingType(title='web application',
		description='web applications')
	t.save()
	t = models.ListingType(title='widgets',
		description='widget things')
	t.save()

	# Intents

	# Organizations

	# Stewards

	# Notifications

