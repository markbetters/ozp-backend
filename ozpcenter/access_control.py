"""
Access control
"""

def set_access_control(entitlement_data, username):
	"""
	Given entitlement data from an external authorization service, set this
	user's access control

	entitlement_data: {
		clearance: ['UNCLASSIFIED', 'SECRET'],
		accesses: ['SI'],
		legacy_accesses: ['ABC', 'XYZ'],
		visa: ['USA', 'OTHERS']
	}
	"""
	pass

def has_access(users_access_control, access_control):
	"""
	Determine if a user has access to a given access control

	Ultimately, this will likely invoke a separate service to do the check.
	For now, some basic logic will suffice

	Assume the access control is of the format:
	<CLASSIFICATION>//<CONTROL>//<CONTROL>//...
	"""
	# make sure base classifications are compatible

	# make sure controls are compatible
	return True