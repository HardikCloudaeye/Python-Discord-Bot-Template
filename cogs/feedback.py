import discord
from discord.ext import commands
from discord.ext.commands import Context
import json
import os
from typing import Optional

class FeedbackCog(commands.Cog, name="feedback"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(
        name="submit_feedback",
        description="Submit feedback or suggestion for the server"
    )
    async def submit_feedback(
        self,
        context: Context,
        feedback: str
    ) -> None:
        """
        Submit feedback that will be stored for admins to review.

        :param context: The context of the slash command
        :param feedback: The feedback text to submit
        """
      
        await self.bot.database.execute(
            """INSERT INTO feedback (user_id, username, content, timestamp, status)
               VALUES (?, ?, ?, datetime('now'), 'new')""",
            (str(context.author.id), context.author.name, feedback)
        )
        await self.bot.database.commit()
        
        embed = discord.Embed(
            description="Thank you for your feedback!",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.slash_command(
        name="view_feedback",
        description="Generate HTML report of all feedback (Admin only)"
    )
    @commands.has_permissions(administrator=True)
    async def view_feedback(self, context: Context) -> None:
        """
        Generate and send an HTML report of all feedback.
        
        :param context: The context of the slash command
        """
        # Fetch all feedback
        async with self.bot.database.execute(
            "SELECT username, content, timestamp FROM feedback"
        ) as cursor:
            entries = await cursor.fetchall()
        

        html_content = """
        <html>
        <head>
            <style>
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                th { background-color: #9C84EF; color: white; }
            </style>
        </head>
        <body>
            <h1>Feedback Dashboard</h1>
            <table>
                <tr>
                    <th>User</th>
                    <th>Feedback</th>
                    <th>Time</th>
                </tr>
        """
        
        for username, content, timestamp in entries:
           
            html_content += f"""
                <tr>
                    <td>{username}</td>
                    <td>{content}</td>
                    <td>{timestamp}</td>
                </tr>
            """
            
        html_content += "</table></body></html>"
        
        # Save and send report
        report_path = f"{os.path.realpath(os.path.dirname(__file__))}/feedback_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        await context.send(
            file=discord.File(report_path),
            embed=discord.Embed(
                description="Feedback report generated!",
                color=0x9C84EF
            )
        )
        
        # Cleanup
        os.remove(report_path)

async def setup(bot):
    # Create feedback table if it doesn't exist
    await bot.database.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    await bot.database.commit()
    
    await bot.add_cog(FeedbackCog(bot))
