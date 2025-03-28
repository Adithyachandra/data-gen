import os
import json
from datetime import datetime
from dotenv import load_dotenv
import subprocess

def run_curl_command(cmd):
    """Run a curl command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return None

def fetch_jira_data():
    """Fetch users and teams from JIRA"""
    # Load environment variables
    load_dotenv()
    
    # Get JIRA credentials
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    project_key = os.getenv('JIRA_PROJECT_KEY')
    org_id = os.getenv('JIRA_ORG_ID')
    
    if not all([jira_url, jira_username, jira_api_token, project_key, org_id]):
        raise ValueError("Missing required environment variables. Please check your .env file.")
    
    # Create output directory if it doesn't exist
    os.makedirs('jira_data', exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Fetch users
    print("\nFetching users from JIRA...")
    users_cmd = f'curl -s -X GET -u {jira_username}:{jira_api_token} -H "Accept: application/json" "{jira_url}/rest/api/3/users/search"'
    users_response = run_curl_command(users_cmd)
    
    if not users_response:
        print("Failed to fetch users")
        return
    
    print("\nRaw users response:")
    print(users_response[:200] + "...")
    
    try:
        users_data = json.loads(users_response)
        # Extract relevant user information
        users = [{
            'accountId': user.get('accountId'),
            'displayName': user.get('displayName'),
            'emailAddress': user.get('emailAddress'),
            'active': user.get('active', True),
            'timeZone': user.get('timeZone'),
            'locale': user.get('locale')
        } for user in users_data]
        
        # Save users data
        users_file = f'jira_data/jira_users_{timestamp}.json'
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"\nUsers data saved to {users_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing users JSON: {str(e)}")
    
    # Fetch project roles (teams)
    print("\nFetching project roles from JIRA...")
    roles_cmd = f'curl -s -X GET -u {jira_username}:{jira_api_token} -H "Accept: application/json" "{jira_url}/rest/api/3/project/{project_key}/role"'
    roles_response = run_curl_command(roles_cmd)
    
    if not roles_response:
        print("Failed to fetch project roles")
        return
    
    print("\nRaw roles response:")
    print(roles_response[:200] + "...")
    
    try:
        roles_data = json.loads(roles_response)
        # Extract role information
        roles = []
        for role_name, role_url in roles_data.items():
            # Fetch detailed role information
            role_cmd = f'curl -s -X GET -u {jira_username}:{jira_api_token} -H "Accept: application/json" "{role_url}"'
            role_response = run_curl_command(role_cmd)
            if role_response:
                try:
                    role_info = json.loads(role_response)
                    roles.append({
                        'name': role_name,
                        'id': role_info.get('id'),
                        'actors': role_info.get('actors', []),
                        'scope': role_info.get('scope', {})
                    })
                except json.JSONDecodeError:
                    print(f"Error parsing role JSON for {role_name}")
        
        # Save roles data
        roles_file = f'jira_data/jira_roles_{timestamp}.json'
        with open(roles_file, 'w') as f:
            json.dump(roles, f, indent=2)
        print(f"\nProject roles data saved to {roles_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing roles JSON: {str(e)}")
    
    # Fetch teams using Teams Public REST API
    print("\nFetching teams from JIRA...")
    teams_cmd = f'curl -s -X GET -u {jira_username}:{jira_api_token} -H "Accept: application/json" "{jira_url}/gateway/api/public/teams/v1/org/{org_id}/teams"'
    teams_response = run_curl_command(teams_cmd)
    
    if not teams_response:
        print("Failed to fetch teams")
        return
    
    print("\nRaw teams response:")
    print(teams_response[:200] + "...")
    
    try:
        teams_data = json.loads(teams_response)
        print("\nTeams data structure:")
        print(json.dumps(teams_data, indent=2)[:500] + "...")
        
        # Extract relevant team information
        teams = []
        if 'entities' in teams_data:
            print(f"\nFound {len(teams_data['entities'])} teams in response")
            for team in teams_data['entities']:
                team_id = team.get('teamId')
                print(f"\nProcessing team: {team.get('displayName')} (ID: {team_id})")
                
                # Fetch team members for each team
                members_cmd = f'curl -s -X POST -u {jira_username}:{jira_api_token} -H "Accept: application/json" -H "Content-Type: application/json" -d \'{{"first": 50}}\' "{jira_url}/gateway/api/public/teams/v1/org/{org_id}/teams/{team_id}/members"'
                members_response = run_curl_command(members_cmd)
                
                team_info = {
                    'id': team_id,
                    'name': team.get('displayName'),
                    'description': team.get('description'),
                    'teamType': team.get('teamType'),
                    'members': []
                }
                
                if members_response:
                    try:
                        members_data = json.loads(members_response)
                        print(f"Found {len(members_data.get('results', []))} members for team {team.get('displayName')}")
                        team_info['members'] = [{
                            'accountId': member.get('accountId'),
                            'displayName': member.get('displayName'),
                            'emailAddress': member.get('emailAddress')
                        } for member in members_data.get('results', [])]
                    except json.JSONDecodeError:
                        print(f"Error parsing members JSON for team {team_id}")
                else:
                    print(f"No members response for team {team_id}")
                
                teams.append(team_info)
                print(f"Added team {team.get('displayName')} to teams list")
        else:
            print("\nNo 'entities' key found in response data")
            print("Available keys:", list(teams_data.keys()))
        
        # Save teams data
        teams_file = f'jira_data/jira_teams_{timestamp}.json'
        with open(teams_file, 'w') as f:
            json.dump(teams, f, indent=2)
        print(f"\nTeams data saved to {teams_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing teams JSON: {str(e)}")
    
    # Print summary
    print("\nData Fetch Summary:")
    print(f"Total Users: {len(users) if 'users' in locals() else 0}")
    print(f"Total Project Roles: {len(roles) if 'roles' in locals() else 0}")
    print(f"Total Teams: {len(teams) if 'teams' in locals() else 0}")

if __name__ == "__main__":
    fetch_jira_data() 