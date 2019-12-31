def validate_user_fields(fields):
    if 'username' in fields and 'password' in fields:
        print(fields)

        username = fields['username']
        password = fields['password']

        return { 
          'username': username, 
          'password': password }

    elif 'username' in fields:
        return { 
          'username': fields['username'],
          'password': None,
          "errors": {
            "password": "password is missing"} }

    elif 'password' in fields:
        return { 
          'username': None,
          'password': fields['password'],
          "errors": {
            "username": "username is missing"} }

    else:
        return { 
          'username': None,
          'password': None,
          "errors": {
            "username": "username is missing", 
            "password": "password is missing"} }


def stringify_errors(errors):
  stringified = ''
  count = len(errors)

  if count == 1:
    stringified += 'Error: '
    for key in errors:
      stringified += errors[key]
  else:
    stringified += 'Errors: '
    for key in errors:
      stringified += errors[key]
      stringified += ", "

  return stringified
