ne = {}

    # Find all th markers and their positions
    th_markers = [(i, e) for i, e in enumerate(timeline_elements) if 'th' in e]

    # Process each over
    for i, (pos, marker) in enumerate(th_markers):
        over_num = int(marker.split('th')[0])
        # First ball is the digit after 'th'
        first_ball = marker[-1]
        # Next 5 balls after the marker
        rest_balls = timeline_elements[pos+1:pos+6]
        timeline[f"{over_num}th"] = [first_ball] + rest_balls

    # Handle highest over (balls before first th)
    if th_markers:
        highest_over = max(int(k.split('th')[0]) for k in timeline.keys())
        first_th_pos = th_markers[0][0]
        if first_th_pos > 0:
            timeline[f"{highest_over+1}th"] = timeline_elements[:first_th_pos]

    # Sort in descending order
    timeline = dict(