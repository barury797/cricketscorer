import sqlite3
import asyncio

db = sqlite3.connect("cricket_guru/cricketguru.db")
cursor = db.cursor()

async def get_head_to_head(team1, team2):
    # Basic query to get all matches between these teams
    query = """
    SELECT
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS team1_wins,
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS team2_wins,
        
        (SELECT MAX(team1_runs) || '/' || team1_wickets
         FROM matches
         WHERE team1 = ? AND team2 = ?) AS team1_highest,
         
        (SELECT MAX(team2_runs) || '/' || team2_wickets
         FROM matches
         WHERE team1 = ? AND team2 = ?) AS team2_highest,
         
        (SELECT MIN(team1_runs) || '/' || team1_wickets
         FROM matches
         WHERE team1 = ? AND team2 = ? AND team1_runs > 0) AS team1_lowest,
         
        (SELECT MIN(team2_runs) || '/' || team2_wickets
         FROM matches
         WHERE team1 = ? AND team2 = ? AND team2_runs > 0) AS team2_lowest,
         
        ROUND(AVG(CASE WHEN team1 = ? THEN team1_runs
                      WHEN team2 = ? THEN team2_runs END), 2) AS team1_avg,
                      
        ROUND(AVG(CASE WHEN team1 = ? THEN team1_runs
                      WHEN team2 = ? THEN team2_runs END), 2) AS team2_avg
    FROM matches
    WHERE (team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)
    """
    
    cursor.execute(query, (
        team1, team2,              # For team1_wins and team2_wins
        team1, team2,              # For team1_highest (when team1 is first)
        team2, team1,              # For team2_highest (when team2 is first) 
        team1, team2,              # For team1_lowest (when team1 is first)
        team2, team1,              # For team2_lowest (when team2 is first)
        team1, team2,              # For team1_avg (both positions)
        team2, team1,              # For team2_avg (both positions)
        team1, team2, team2, team1 # For WHERE clause
    ))
    
    return cursor.fetchone()

if __name__ == "__main__":
    async def main():
        result = await get_head_to_head("rt", "jg")
        print(result)
    
    asyncio.run(main())