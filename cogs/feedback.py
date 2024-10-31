import disnake
from disnake.ext import commands
import sqlite3
import json
from datetime import datetime

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize SQLite database
        self.conn = sqlite3.connect('feedback.db')
        self.setup_database()

    def setup_database(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                username TEXT,
                content TEXT,
                timestamp TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def store_feedback(self, user_id, username, content):
        """Store user feedback in database"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO feedback (user_id, username, content, timestamp, status) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, content, datetime.now().isoformat(), 'new')
        )
        self.conn.commit()

    @commands.slash_command(
        name="submit_feedback",
        description="Submit feedback or suggestion for the server"
    )
    async def submit_feedback(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        feedback: str
    ):
        """Handle feedback submission"""
        self.store_feedback(str(inter.author.id), inter.author.name, feedback)
        await inter.response.send_message("Thank you for your feedback!", ephemeral=True)

    @commands.slash_command(
        name="view_feedback",
        description="View all feedback (Admin only)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def view_feedback(self, inter: disnake.ApplicationCommandInteraction):
        """Display all feedback entries"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, content, timestamp FROM feedback')
        entries = cursor.fetchall()
        
      
        html_content = "<html><body><h1>Feedback Dashboard</h1><table>"
        for username, content, timestamp in entries:
            html_content += f"""
                <tr>
                    <td>{username}</td>
                    <td>{content}</td>
                    <td>{timestamp}</td>
                </tr>
            """
        html_content += "</table></body></html>"
        
        # Save the HTML report
        with open('feedback_report.html', 'w') as f:
            f.write(html_content)
            
        await inter.response.send_message(
            "Feedback report generated!",
            file=disnake.File('feedback_report.html'),
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(Feedback(bot))
