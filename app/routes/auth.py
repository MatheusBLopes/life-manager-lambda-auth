import json

from aws_lambda_powertools import Logger

logger = Logger(service="LifeManagerLambdaAuth")

class Auth():
    def __init__(self, boto_client, payload, cognito_client_id):
        self.boto_client = boto_client
        self.payload = payload
        self.cognito_client_id = cognito_client_id
    
    def login(self):
        try:
            logger.info("Acessando usename e senha")
            username = self.payload['username']
            password = self.payload['password']
        except KeyError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Please, provide username and password correctly'})
            }

        try:
            logger.info("Fazendo request para o cognito")
            response = self.boto_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            logger.info(f"Resultado da autenticação: {response}")
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        except self.boto_client.exceptions.NotAuthorizedException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid username or password'})
            }
        except self.boto_client.exceptions.UserNotFoundException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'User not found'})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': str(e)})
            }

    def change_password(self):
        try:
            logger.info("Acessando username, old_password e new_password")
            username = self.payload['username']
            old_password = self.payload['old_password']
            new_password = self.payload['new_password']
        except KeyError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Please, provide username, old_password, and new_password correctly'})
            }

        try:
            logger.info("Fazendo request para o cognito para autenticar o usuário")
            auth_response = self.boto_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': old_password
                }
            )
            access_token = auth_response.get('AuthenticationResult')

            logger.info("Fazendo request para o cognito para mudar a senha")
            self.boto_client.change_password(
                AccessToken=access_token,
                PreviousPassword=old_password,
                ProposedPassword=new_password
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Password changed successfully'})
            }
        except self.boto_client.exceptions.NotAuthorizedException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid username or password'})
            }
        except self.boto_client.exceptions.UserNotFoundException:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'User not found'})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': str(e)})
            }

    def reset_temporary_password(self):
        try:
            logger.info("Acessando username, temporary_password e new_password")
            username = self.payload['username']
            temp_password = self.payload['temporary_password']
            new_password = self.payload['new_password']
        except KeyError as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Please, provide username, temporary_password, and new_password correctly'})
            }

        try:
            # Step 1: Initiate Auth with Temporary Credentials
            auth_response = self.boto_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": temp_password,
                }
            )

            # Step 2: Handle NEW_PASSWORD_REQUIRED challenge
            if "ChallengeName" in auth_response and auth_response["ChallengeName"] == "NEW_PASSWORD_REQUIRED":
                session = auth_response["Session"]

                response = self.boto_client.respond_to_auth_challenge(
                    ClientId=self.cognito_client_id,
                    ChallengeName="NEW_PASSWORD_REQUIRED",
                    Session=session,
                    ChallengeResponses={
                        "USERNAME": username,
                        "NEW_PASSWORD": new_password,
                    }
                )
                return {
                    "message": "Password changed successfully",
                    "access_token": response["AuthenticationResult"]["AccessToken"],
                    "id_token": response["AuthenticationResult"]["IdToken"],
                    "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                }

            return {"error": "Unexpected response from Cognito"}

        except self.boto_client.exceptions.NotAuthorizedException as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}