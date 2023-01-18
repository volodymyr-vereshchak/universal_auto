import requests
import logging

logger = logging.getLogger("portmone")

class GatewayError(Exception):
    """Raised when API http request failed."""
    pass


class StatusCodeError(Exception):
    """Raised when API returns non-200 status code."""


class Portmone():
    def __init__(self, sum: float, commission=None):
        # Type sum and commission : float
        self.sum = sum
        self.commission = commission

    def user_commission(self):
        return self.sum - self.commission

    def portmone_commission(self):
        return self.sum - (self.sum * 0.01) - 5

    def get_commission(self):
        if self.commission is None:
            commission = self.portmone_commission()
            return commission
        else:
            commission = self.user_commission()
            return commission

    @classmethod
    def _make_request(cls, url: str, payload: dict) -> dict:
        """Make request to API gateway.
        Raises:
            GatewayError: If no the API response.
            StatusCodeError: If the API response code is't 200.
        """
        try:
            response = requests.post(url, json=payload)
        except Exception as error:
            raise GatewayError

        if response.status_code != 200:
            raise StatusCodeError(code=response.status_code, message=response.content)

        return response.json()

    def get_link(self):
        url = 'https://www.portmone.com.ua/gateway/'
        payload = {
                "method":"getLinkInvoice",
                "params": {
                        "data":{
                            "login": os.environ["PORTMONE_LOGIN"],
                            "password":os.environ["PORTMONE_PASSWORD"],
                            "payeeId":os.environ["PORTMONE_PAYEE_ID"],
                            "amount": str(self.get_commission()),
                            }
                },
                "id": "1"
        }

        result = self._make_request(url, payload)
        if result:
            try:
                result: dict = result['result']['linkInvoice']
                return result
            except IndexError:
                logger.error(f"Failed to get link")
                return None

    @staticmethod
    def conversion_to_float(sum) -> float:
    # input type sum int or str
        try:
            d = float(sum)
            return d
        except ValueError:
            return None


