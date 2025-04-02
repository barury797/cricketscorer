import sqlite3
import asyncio

db = sqlite3.connect("g:/cricket/cricketscorer/cricket_guru/cricketguru.db")
cursor = db.cursor()

def overs_to_balls(overs):
    if isinstance(overs, (int, float)):
        full_overs = int(overs)
        decimal_part = overs - full_overs
        return full_overs * 6 + int(decimal_part * 10)
    elif isinstance(overs, str) and '.' in overs:
        full_overs, balls = overs.split('.')
        return int(full_overs) * 6 + int(balls)
    else:
        try:
            return int(overs) * 6
        except:
            return 0

async def get_head_to_head(team1, team2):
    query = """
    SELECT
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS team1_wins,
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS team2_wins,
        (SELECT MAX(team1_runs) || '/' || team1_wickets FROM matches WHERE team1 = ? AND team2 = ?) AS team1_highest,
        (SELECT MAX(team2_runs) || '/' || team2_wickets FROM matches WHERE team1 = ? AND team2 = ?) AS team2_highest,
        (SELECT MIN(team1_runs) || '/' || team1_wickets FROM matches WHERE team1 = ? AND team2 = ? AND team1_runs > 0) AS team1_lowest,
        (SELECT MIN(team2_runs) || '/' || team2_wickets FROM matches WHERE team1 = ? AND team2 = ? AND team2_runs > 0) AS team2_lowest,
        ROUND(AVG(CASE WHEN team1 = ? THEN team1_runs WHEN team2 = ? THEN team2_runs END), 2) AS team1_avg,
        ROUND(AVG(CASE WHEN team1 = ? THEN team1_runs WHEN team2 = ? THEN team2_runs END), 2) AS team2_avg
    FROM matches
    WHERE (team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?)
    """
    cursor.execute(query, (team1, team2, team1, team2, team2, team1, team1, team2, team2, team1, team1, team2, team2, team1, team1, team2, team2, team1))
    return cursor.fetchone()

async def get_team_record(team_name):
    query = """
    SELECT
        SUM(CASE WHEN winner = ? THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN (team1 = ? OR team2 = ?) AND winner != ? AND winner IS NOT NULL THEN 1 ELSE 0 END) AS losses
    FROM matches
    WHERE team1 = ? OR team2 = ?
    """
    cursor.execute(query, (team_name, team_name, team_name, team_name, team_name, team_name))
    result = cursor.fetchone()
    return (result[0] or 0, result[1] or 0)

async def add_match(match_date, total_overs, team1, team1_score, team1_overs, team2, team2_score, team2_overs, winner):
    try:
        total_balls = overs_to_balls(total_overs)
        team1_balls = overs_to_balls(team1_overs)
        team2_balls = overs_to_balls(team2_overs)

        team1_runs, team1_wickets = map(int, team1_score.split("/"))
        team2_runs, team2_wickets = map(int, team2_score.split("/"))
        
        cursor.execute('''INSERT INTO matches (
            match_date, total_balls, team1, team1_runs, team1_wickets, team1_balls,
            team2, team2_runs, team2_wickets, team2_balls, winner
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            match_date, total_balls, team1, team1_runs, team1_wickets, team1_balls,
            team2, team2_runs, team2_wickets, team2_balls, winner
        ))
        db.commit()
        return True
    except Exception as e:
        print(f"Error adding match: {e}")
        db.rollback()
        return False

async def main():
    print(await get_head_to_head("rt", "jg"))
    print(await get_team_record("rt"))
    
    result = await add_match(
        match_date="2025-04-02",
        total_overs="20",
        team1="rt",
        team1_score="165/6",
        team1_overs="20",
        team2="jg",
        team2_score="152/8",
        team2_overs="20",
        winner="rt"
    )
    print(f"Match added: {result}")

if __name__ == "__main__":
    asyncio.run(main())