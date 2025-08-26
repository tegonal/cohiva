from rocketchat_API.rocketchat import RocketChat


class RocketChatContrib(RocketChat):
    """
    Implement API calls that are missing in rocketchat_API
    """

    def contrib_add_team_members(self, team_name, members, **kwargs):
        """Add members to a team. Requires add-team-member or edit-team-member permission."""
        return self.call_api_post(
            "teams.addMembers", teamName=team_name, members=members, kwargs=kwargs
        )

    def contrib_get_team_members(self, team_name, **kwargs):
        """List all teams members."""
        return self.call_api_get("teams.members", teamName=team_name, kwargs=kwargs)

    def contrib_list_all_teams(self, **kwargs):
        """List all teams with info. Requires view-all-teams permission."""
        return self.call_api_get("teams.listAll", kwargs=kwargs)

    def contrib_remove_team_member(self, team_name, user_id, **kwargs):
        """Remove member from team. Requires edit-team-member permission."""
        return self.call_api_post(
            "teams.removeMember", teamName=team_name, userId=user_id, kwargs=kwargs
        )
