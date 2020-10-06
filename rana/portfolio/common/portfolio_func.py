from rana.common.exceptions.exceptions import DataValidationError
from rana.portfolio.models import Portfolio


def portfolio_put_validation(request_data, open_id):
    if 'id' not in request_data:
        raise DataValidationError('Required parameter is not found', 'id')

    if 'content' not in request_data:
        raise DataValidationError('Required parameter is not found', 'content')

    if not Portfolio.objects.filter(id=request_data['id'],
                                    open_id=open_id).exists():
        raise DataValidationError('No such portfolio exists', 'Not belongs to you')
