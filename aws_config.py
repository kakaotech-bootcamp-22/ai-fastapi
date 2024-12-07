import boto3
import os

def get_ssm_parameter(parameter_name: str, with_decryption: bool = False) -> str:
    """
    AWS SSM 파라미터 스토어에서 지정된 파라미터 값을 가져옵니다.

    Args:
        parameter_name (str): 가져올 파라미터의 경로.
        with_decryption (bool): 암호화된 파라미터를 복호화할지 여부. 기본값은 False.

    Returns:
        str: 파라미터 값.
    """
    ssm_client = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'ap-northeast-2'))
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=with_decryption  # 암호화되지 않았다면 False로 설정
        )
        return response['Parameter']['Value']
    except Exception as e:
        raise Exception(f"Error fetching parameter {parameter_name}: {str(e)}")


# # Example usage
# if __name__ == "__main__":
#     # 두 가지 파라미터 경로
#     backend_url_param = "/config/ktb22/backend.server.url"
#     openai_key_param = "/config/ktb22/OPENAI_API_KEY"
#
#     # 각 파라미터 값 가져오기
#     try:
#         backend_url = get_ssm_parameter(backend_url_param)
#         openai_api_key = get_ssm_parameter(openai_key_param)
#
#         print(f"Backend URL: {backend_url}")
#         print(f"OpenAI API Key: {openai_api_key}")
#     except Exception as e:
#         print(f"Error: {e}")
