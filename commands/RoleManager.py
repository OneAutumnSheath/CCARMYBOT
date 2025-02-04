async def role_update(self):
    """Überprüft die Mitglieder jeder Rolle und speichert die Information."""
    roles = load_roles()
    config = load_config()

    # Stellen Sie sicher, dass die Konfiguration korrekt geladen wurde
    if not config.get("channels"):
        print("Keine Channels in der Konfiguration gefunden.")
        return  # Wenn keine Channels in der Konfiguration gefunden wurden, breche ab

    # Hole die Channels für diese Guild
    if str(self.guild_id) in config["channels"]:
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return  # Wenn der Bot nicht im richtigen Server ist, breche ab

        for channel_id, channel_data in config["channels"][str(self.guild_id)].items():
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                continue  # Falls der Channel nicht existiert, überspringen

            # Hole die Rollen in diesem Channel
            for role_name, members in channel_data["roles"].items():
                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    continue  # Falls die Rolle nicht gefunden wird, überspringen
                
                # Hole alle Mitglieder mit dieser Rolle
                role_members = [member.id for member in role.members]
                channel_data["roles"][role_name] = role_members

            # Speichern der aktuellen Rollen und Mitglieder für den Channel
            save_roles(roles)

            # Erstelle ein Embed mit den Rollenmitgliedern für den Channel
            embed = discord.Embed(title=f"Rollen Mitglieder Update: {channel.name}", color=discord.Color.blue())
            for role_name, member_ids in channel_data["roles"].items():
                members = [f"<@{member_id}>" for member_id in member_ids]
                embed.add_field(name=role_name, value="\n".join(members), inline=False)

            embed.set_footer(text=f"Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await channel.send(embed=embed)
async def setup(bot):
    await bot.add_cog(RoleManager(bot))