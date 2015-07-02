"""
Access control utilities

An access control is a string of the format:
<CLASSIFICATION>//CONTROL1//CONTROL2//...

For example:
SECRET//ABC//XYZ//USA or TOP SECRET or UNCLASSIFIED//FOUO

In reality, access controls are not this simple, but this trivial implementation
will suffice for now, and can easily support dispatching to external services
containing the real logic to do this right

This simple logic is this: for a user to have access:
	1. They must have a classification equal to or higher than that required
	2. They must have at least all controls that are required (in any order)
"""

def generate_access_control(entitlement_data):
	"""
	Given entitlement data from an external authorization service, generate
	access control string

	Ultimately, this will likely invoke a separate service to do the check.
	For now, some basic logic will suffice

	entitlement_data: {
		clearance: ['UNCLASSIFIED', 'CONFIDENTIAL', 'SECRET'],
		accesses: ['SI'],
		legacy_accesses: ['ABC', 'XYZ'],
		visa: ['USA', 'OTHERS']
	}
	"""
	# TODO: check that entitlement_data structure is valid
	access_control = ''
	# first, extract the highest clearance
	if 'TOP SECRET' in entitlement_data['clearance']:
		access_control += 'TOP SECRET'
	elif 'SECRET' in entitlement_data['clearance']:
		access_control += 'SECRET'
	elif 'CONFIDENTIAL' in entitlement_data['clearance']:
		access_control += 'CONFIDENTIAL'
	elif 'UNCLASSIFIED' in entitlement_data['clearance']:
		access_control += 'UNCLASSIFIED'
	else:
		# TODO: handle error
		pass
	access_control += '//'

	controls = entitlement_data['accesses'] + \
		entitlement_data['legacy_accesses'] + entitlement_data['visa']
	for i in controls:
		access_control += '%s//' % i

	# remove last '//' from string
	access_control = access_control[:-2]
	return access_control

def has_access(user_access_controls, required_access_controls):
	"""
	Determine if a user has access to a given access control

	Ultimately, this will likely invoke a separate service to do the check.
	For now, some basic logic will suffice

	Assume the access control is of the format:
	<CLASSIFICATION>//<CONTROL>//<CONTROL>//...
	"""
	user_controls = user_access_controls.split('//')
	required_access_controls = required_access_controls.split('//')
	# make sure base classifications are compatible
	user_classification = user_controls[0]
	required_classification = required_access_controls[0]
	if required_classification == 'UNCLASSIFIED':
		pass
	elif required_classification == 'CONFIDENTIAL':
		if user_classification not in ['CONFIDENTIAL', 'SECRET', 'TOP SECRET']:
			return False
	elif required_classification == 'SECRET':
		if user_classification not in ['SECRET', 'TOP SECRET']:
			return False
	elif required_classification == 'TOP SECRET':
		if user_classification != 'TOP SECRET':
			return False
	else:
		return False

	# make sure controls are compatible
	user_controls = user_controls[1:]
	required_controls = required_access_controls[1:]
	missing_controls = [i for i in required_controls if i not in user_controls]
	if not missing_controls:
		return True
	else:
		return False