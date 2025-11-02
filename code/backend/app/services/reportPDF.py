"""
PDF Report generation service
"""
import io
import base64
import json
import html as html_module
from datetime import datetime
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
from weasyprint import HTML
from app.state import QuestionState
from app.services.report import get_whole_Report


async def generate_pdf_report(question_state: QuestionState) -> bytes:
    """
    Generate a PDF report from the question state
    
    Args:
        question_state: The QuestionState to generate report for
        
    Returns:
        bytes: PDF file as bytes
    """
    # Get report data
    report_data = await get_whole_Report(question_state)
    
    # Generate scatter plot image as base64
    plot_image = _generate_scatter_plot_image(report_data["results"], question_state)
    
    # Calculate statistics
    stats = _calculate_statistics(question_state, report_data)
    
    # Generate HTML
    html_content = _generate_html_report(
        question_state=question_state,
        report_data=report_data,
        plot_image=plot_image,
        stats=stats
    )
    
    # Convert HTML to PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    if pdf_bytes is None:
        raise ValueError("Failed to generate PDF")
    return pdf_bytes


def _generate_scatter_plot_image(results: List[Dict], question_state: QuestionState) -> str:
    """Generate scatter plot and return as base64 encoded image"""
    # Define colors for clusters (matching frontend)
    cluster_colors = {
        "Priority Ranking": "#a855f7",  # Purple
        "Lottery Allocation": "#10b981",  # Green
        "Collaborative Allocation": "#ec4899",  # Pink
        "Room Selection": "#6b7280",  # Gray
    }
    
    # Get unique cluster labels
    unique_clusters = question_state.two_word_summaries or []
    
    # Create plot - compact size for 2-page PDF
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_facecolor('#FFFFFF')
    
    # Plot points by cluster
    for cluster_label in unique_clusters:
        cluster_results = [r for r in results if r.get("two_word_summary") == cluster_label]
        if not cluster_results:
            continue
        
        # Get color for this cluster (fallback if not in predefined)
        color = cluster_colors.get(cluster_label, "#6b7280")
        
        x_coords = [r["x"] for r in cluster_results]
        y_coords = [r["y"] for r in cluster_results]
        
        ax.scatter(x_coords, y_coords, c=color, s=25, alpha=0.6, label=cluster_label)
    
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('auto')
    ax.axis('off')  # Remove axes as shown in image
    
    # Save to bytes with lower DPI for smaller file size
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=90, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode()
    return img_base64


def _calculate_statistics(question_state: QuestionState, report_data: Dict) -> Dict[str, Any]:
    """Calculate statistics for the report"""
    messages = question_state.discord_messages
    
    # Count participants
    unique_users = set(msg.user_id for msg in messages)
    
    # Opinion distribution
    positive = sum(1 for msg in messages if msg.classification == "positive")
    negative = sum(1 for msg in messages if msg.classification == "negative")
    neutral = sum(1 for msg in messages if (msg.classification == "neutral" or not msg.classification))
    
    # Top discussion themes (clusters)
    cluster_counts = {}
    for msg in messages:
        cluster = msg.two_word_summary or "Unassigned"
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
    
    # Sort by count and get top themes
    sorted_themes = sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)
    top_themes = [
        {"name": name, "count": count, "percentage": round(count / len(messages) * 100) if messages else 0}
        for name, count in sorted_themes[:3]
    ]
    
    return {
        "message_count": len(messages),
        "participant_count": len(unique_users),
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "top_themes": top_themes
    }


def _generate_html_report(
    question_state: QuestionState,
    report_data: Dict,
    plot_image: str,
    stats: Dict
) -> str:
    """Generate HTML content for the PDF"""
    
    summary = report_data.get("summary", {})
    if isinstance(summary, str):
        try:
            summary = json.loads(summary) if summary else {}
        except json.JSONDecodeError:
            summary = {}
    
    points = summary.get("points", [])
    description = summary.get("description", "")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 10mm;
            }}
            * {{
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                color: #000000;
                background: #ffffff;
                margin: 0;
                padding: 0;
                font-size: 10px;
                line-height: 1.4;
            }}
            .header {{
                background: white;
                border-bottom: 1px solid #d1d5db;
                padding: 8px 12px;
                margin-bottom: 12px;
            }}
            .header-date {{
                color: #374151;
                font-size: 9px;
            }}
            .card {{
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 12px;
                break-inside: avoid;
            }}
            h1, h2, h3, h4 {{
                margin: 0;
                color: #000000;
            }}
            h1 {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            h2 {{
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            h3 {{
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 6px;
            }}
            h4 {{
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 4px;
            }}
            .discussion-overview {{
                border-left: 2px solid #3b82f6;
                padding-left: 10px;
            }}
            .discussion-overview h1 {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #000000;
            }}
            .question {{
                font-size: 12px;
                font-style: italic;
                color: #1f2937;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            .description {{
                color: #374151;
                line-height: 1.5;
                margin-bottom: 12px;
                font-size: 10px;
            }}
            .key-perspectives {{
                margin-top: 12px;
            }}
            .key-perspectives h2 {{
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #000000;
            }}
            .perspective-box {{
                background: #f9fafb;
                border-radius: 8px;
                padding: 8px 10px;
                margin-bottom: 8px;
                border: 1px solid #e5e7eb;
            }}
            .perspective-title {{
                font-weight: 600;
                color: #000000;
                font-size: 11px;
                margin-bottom: 2px;
            }}
            .perspective-rating {{
                color: #4b5563;
                font-size: 9px;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .plot-card {{
                margin-top: 12px;
            }}
            .plot-card h2 {{
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 6px;
                color: #000000;
            }}
            .plot-description {{
                color: #4b5563;
                font-size: 9px;
                margin-bottom: 8px;
            }}
            .legend {{
                display: flex;
                gap: 10px;
                margin-bottom: 8px;
                flex-wrap: wrap;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 9px;
            }}
            .legend-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                flex-shrink: 0;
            }}
            .plot-image {{
                width: 100%;
                height: 400px;
                object-fit: contain;
                border-radius: 8px;
                margin-top: 8px;
            }}
            .insights-card {{
                margin-bottom: 6px;
            }}
            .insights-card h2 {{
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 6px;
                color: #000000;
            }}
            .stats-boxes {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 6px;
                margin-bottom: 6px;
            }}
            .stat-box {{
                background: #f9fafb;
                border-radius: 6px;
                padding: 6px;
                text-align: center;
                border: 1px solid #e5e7eb;
            }}
            .stat-label {{
                font-size: 7px;
                color: #4b5563;
                margin-bottom: 2px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .stat-value {{
                font-size: 16px;
                font-weight: bold;
                color: #000000;
            }}
            .opinion-distribution {{
                margin-bottom: 6px;
            }}
            .opinion-distribution h3 {{
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 4px;
                color: #000000;
            }}
            .opinion-item {{
                background: #f9fafb;
                padding: 5px 6px;
                border-radius: 6px;
                margin-bottom: 3px;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 8px;
                border: 1px solid #e5e7eb;
            }}
            .opinion-dot {{
                width: 7px;
                height: 7px;
                border-radius: 50%;
                flex-shrink: 0;
            }}
            .opinion-dot.positive {{ background: #10b981; }}
            .opinion-dot.negative {{ background: #ef4444; }}
            .opinion-dot.neutral {{ background: #6b7280; }}
            .top-themes {{
                margin-top: 6px;
            }}
            .top-themes h3 {{
                font-size: 11px;
                font-weight: 600;
                margin-bottom: 4px;
                color: #000000;
            }}
            .theme-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 3px;
                padding: 5px 6px;
                background: #f9fafb;
                border-radius: 6px;
                border: 1px solid #e5e7eb;
            }}
            .theme-number {{
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                margin-right: 6px;
                font-size: 9px;
                flex-shrink: 0;
            }}
            .theme-number.one {{ background: #3b82f6; }}
            .theme-number.two {{ background: #a855f7; }}
            .theme-number.three {{ background: #ec4899; }}
            .theme-info {{
                flex: 1;
            }}
            .theme-name {{
                font-weight: 600;
                color: #000000;
                font-size: 10px;
                margin-bottom: 1px;
            }}
            .theme-count {{
                font-size: 8px;
                color: #4b5563;
            }}
            .theme-percentage {{
                font-size: 11px;
                font-weight: bold;
                color: #000000;
            }}
            .solutions-section {{
                margin-top: 4px;
            }}
            .solutions-section h2 {{
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 6px;
                text-align: center;
                color: #000000;
            }}
            .solutions-grid {{
                display: flex;
                flex-direction: column;
                gap: 6px;
            }}
            .solution-card {{
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 8px;
                break-inside: avoid;
                position: relative;
                page-break-inside: avoid;
            }}
            .solution-card.best {{
                background: #fef3c7;
                border: 2px solid #f59e0b;
            }}
            .best-badge {{
                position: absolute;
                top: -8px;
                right: 10px;
                background: #fbbf24;
                color: white;
                padding: 2px 6px;
                border-radius: 9999px;
                font-size: 7px;
                font-weight: bold;
            }}
            .solution-card h3 {{
                font-size: 10px;
                font-weight: bold;
                margin-bottom: 4px;
                color: #000000;
            }}
            .solution-advantages, .solution-challenges {{
                margin-bottom: 4px;
            }}
            .solution-advantages h4, .solution-challenges h4 {{
                font-size: 8px;
                font-weight: 600;
                margin-bottom: 2px;
                color: #1f2937;
            }}
            .advantage-item, .challenge-item {{
                display: flex;
                align-items: start;
                gap: 4px;
                margin-bottom: 1px;
                font-size: 7px;
                color: #374151;
                line-height: 1.2;
            }}
            .advantage-item::before {{
                content: "✓";
                color: #10b981;
                font-weight: bold;
                flex-shrink: 0;
            }}
            .challenge-item::before {{
                content: "✗";
                color: #ef4444;
                font-weight: bold;
                flex-shrink: 0;
            }}
            .approval-rate {{
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid #e5e7eb;
            }}
            .approval-label {{
                font-size: 8px;
                color: #4b5563;
                margin-bottom: 3px;
                font-weight: 600;
            }}
            .approval-bar {{
                height: 6px;
                background: #e5e7eb;
                border-radius: 9999px;
                overflow: hidden;
                margin-bottom: 2px;
            }}
            .approval-fill {{
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #a855f7);
                border-radius: 9999px;
            }}
            .solution-card.best .approval-fill {{
                background: linear-gradient(90deg, #f59e0b, #d97706);
            }}
            .approval-text {{
                font-size: 10px;
                font-weight: bold;
                color: #000000;
            }}
            .experts-section {{
                margin-top: 12px;
                margin-bottom: 12px;
            }}
            .experts-section h2 {{
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #000000;
            }}
            .experts-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            .expert-card {{
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 8px;
                break-inside: avoid;
                page-break-inside: avoid;
            }}
            .expert-header {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 6px;
            }}
            .expert-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #3b82f6;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                font-size: 14px;
            }}
            .expert-info {{
                flex: 1;
            }}
            .expert-name {{
                font-size: 10px;
                font-weight: bold;
                color: #000000;
                margin-bottom: 2px;
            }}
            .expert-cluster {{
                font-size: 7px;
                color: #6b7280;
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
                display: inline-block;
            }}
            .expert-bullets {{
                margin-top: 6px;
                margin-bottom: 6px;
            }}
            .expert-bullets h4 {{
                font-size: 8px;
                font-weight: 600;
                color: #4b5563;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .expert-bullet-item {{
                display: flex;
                align-items: start;
                gap: 4px;
                margin-bottom: 2px;
                font-size: 7px;
                color: #374151;
                line-height: 1.3;
            }}
            .expert-bullet-dot {{
                width: 4px;
                height: 4px;
                border-radius: 50%;
                background: #3b82f6;
                margin-top: 3px;
                flex-shrink: 0;
            }}
            .expert-message {{
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid #e5e7eb;
            }}
            .expert-message h4 {{
                font-size: 8px;
                font-weight: 600;
                color: #4b5563;
                margin-bottom: 3px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .expert-message-text {{
                font-size: 7px;
                color: #6b7280;
                font-style: italic;
                line-height: 1.4;
            }}
            p, span {{
                color: #374151;
                font-size: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-date">
                📅 Generated on {datetime.now().strftime("%B %d, %Y")}
            </div>
        </div>
        
        <div class="card discussion-overview">
            <h1>Discussion Overview</h1>
            <div class="question">"{question_state.question}"</div>
            <div class="description">{description}</div>
            
            <div class="key-perspectives">
                <h2>Key Perspectives</h2>
                {_generate_perspectives_html(points)}
            </div>
        </div>
        
        <!-- Page 1: Discussion Overview + Plot -->
        <div class="card plot-card">
            <h2>Message Clusters</h2>
            <div class="plot-description">Each point represents a message. Hover to see details.</div>
            <div class="legend">
                {_generate_legend_html(question_state.two_word_summaries)}
            </div>
            <img src="data:image/png;base64,{plot_image}" class="plot-image" />
        </div>
        
        <!-- Page 2: Key Insights + Proposed Solutions -->
        <div class="page-break">
            <div class="card insights-card">
                <h2>📊 Key Insights</h2>
                <div class="stats-boxes">
                    <div class="stat-box">
                        <div class="stat-label">MESSAGES</div>
                        <div class="stat-value">{stats['message_count']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">PARTICIPANTS</div>
                        <div class="stat-value">{stats['participant_count']}</div>
                    </div>
                </div>
                
                <div class="opinion-distribution">
                    <h3>Opinion Distribution</h3>
                    <div class="opinion-item">
                        <div class="opinion-dot positive"></div>
                        <span>Positive {stats['positive']}</span>
                    </div>
                    <div class="opinion-item">
                        <div class="opinion-dot negative"></div>
                        <span>Negative {stats['negative']}</span>
                    </div>
                    <div class="opinion-item">
                        <div class="opinion-dot neutral"></div>
                        <span>Neutral {stats['neutral']}</span>
                    </div>
                </div>
                
                <div class="top-themes">
                    <h3>📈 Top Discussion Themes</h3>
                    {_generate_themes_html(stats['top_themes'])}
                </div>
            </div>
            
            {_generate_experts_html(report_data.get("noble_messages", {}))}
        </div>
        
        <!-- Page 3: Proposed Solutions -->
        <div class="page-break">
            <div class="solutions-section">
                <h2>Proposed Solutions</h2>
                <div class="solutions-grid">
                    {_generate_solutions_html(points)}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def _generate_perspectives_html(points: List[Dict]) -> str:
    """Generate HTML for key perspectives"""
    html = ""
    for point in points[:3]:
        title = point.get("title", "")
        rating = point.get("approval_rating", 0)
        rating_pct = int(rating * 100) if isinstance(rating, (int, float)) else 0
        html += f"""
        <div class="perspective-box">
            <div class="perspective-title">{title}</div>
            <div class="perspective-rating">{rating_pct}% approval rating</div>
        </div>
        """
    return html


def _generate_legend_html(clusters: List[str]) -> str:
    """Generate HTML for cluster legend"""
    colors = {
        "Priority Ranking": "#a855f7",  # Purple
        "Lottery Allocation": "#10b981",  # Green
        "Collaborative Allocation": "#ec4899",  # Pink
        "Room Selection": "#6b7280",  # Gray
    }
    html = ""
    for cluster in clusters:
        color = colors.get(cluster, "#6b7280")
        html += f"""
        <div class="legend-item">
            <div class="legend-dot" style="background: {color};"></div>
            <span>{cluster}</span>
        </div>
        """
    return html


def _generate_themes_html(themes: List[Dict]) -> str:
    """Generate HTML for top themes"""
    html = ""
    colors = ["one", "two", "three"]
    for i, theme in enumerate(themes[:3]):
        color_class = colors[i] if i < len(colors) else "one"
        html += f"""
        <div class="theme-item">
            <div class="theme-number {color_class}">{i+1}</div>
            <div class="theme-info">
                <div class="theme-name">{theme['name']}</div>
                <div class="theme-count">{theme['count']} messages</div>
            </div>
            <div class="theme-percentage">{theme['percentage']}%</div>
        </div>
        """
    return html


def _generate_solutions_html(points: List[Dict]) -> str:
    """Generate HTML for proposed solutions cards"""
    html = ""
    if not points:
        return html
    
    # Find the best solution (highest approval rating)
    sorted_points = sorted(points[:3], key=lambda p: p.get("approval_rating", 0), reverse=True)
    best_rating = sorted_points[0].get("approval_rating", 0) if sorted_points else 0
    
    for point in sorted_points:
        title = point.get("title", "")
        pros = point.get("pros", [])
        cons = point.get("cons", [])
        rating = point.get("approval_rating", 0)
        rating_pct = int(rating * 100) if isinstance(rating, (int, float)) else 0
        is_best = rating == best_rating and best_rating > 0
        
        pros_html = "".join(f'<div class="advantage-item">{pro}</div>' for pro in pros)
        cons_html = "".join(f'<div class="challenge-item">{con}</div>' for con in cons)
        
        best_badge = '<div class="best-badge">BEST</div>' if is_best else ''
        card_class = 'solution-card best' if is_best else 'solution-card'
        
        html += f"""
        <div class="{card_class}">
            {best_badge}
            <h3>{title}</h3>
            <div class="solution-advantages">
                <h4>Advantages</h4>
                {pros_html}
            </div>
            <div class="solution-challenges">
                <h4>Challenges</h4>
                {cons_html}
            </div>
            <div class="approval-rate">
                <div class="approval-label">Approval Rate</div>
                <div class="approval-bar">
                    <div class="approval-fill" style="width: {rating_pct}%;"></div>
                </div>
                <div class="approval-text">{rating_pct}%</div>
            </div>
        </div>
        """
    return html


def _generate_experts_html(noble_messages: Dict[str, Dict[str, Any]]) -> str:
    """Generate HTML for cluster experts section"""
    if not noble_messages:
        return ""
    
    experts = list(noble_messages.values())
    if not experts:
        return ""
    
    # Color palette matching frontend
    cluster_colors = [
        "#3b82f6",  # Blue
        "#a855f7",  # Purple
        "#22c55e",  # Green
        "#f59e0b",  # Amber
    ]
    
    html_content = '<div class="experts-section">'
    html_content += '<h2>👥 Cluster Experts</h2>'
    html_content += '<div class="experts-grid">'
    
    for index, expert in enumerate(experts):
        color = cluster_colors[index % len(cluster_colors)]
        username = expert.get("username", "Unknown")
        cluster_label = expert.get("cluster_label", expert.get("cluster", ""))
        profile_pic_url = expert.get("profile_pic_url", "")
        bullets = expert.get("bulletpoint", [])
        message_content = expert.get("message_content", "")
        
        # Generate avatar HTML (use initial if no image)
        initial = username[0].upper() if username else "?"
        
        # For PDF, we'll use a simpler approach - just use initial in a colored circle
        # since external images may not work in WeasyPrint
        avatar_html = f'<div class="expert-avatar" style="border-color: {color}; background: {color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;">{initial}</div>'
        
        # Generate bullets HTML
        bullets_html = ""
        if bullets:
            for bullet in bullets[:3]:  # Limit to 3 bullets
                safe_bullet = html_module.escape(bullet)
                bullets_html += f'<div class="expert-bullet-item"><div class="expert-bullet-dot" style="background: {color};"></div><span>{safe_bullet}</span></div>'
        
        # Escape HTML entities for safety
        safe_username = html_module.escape(username)
        safe_cluster_label = html_module.escape(cluster_label)
        safe_message_content = html_module.escape(message_content)
        
        html_content += f"""
        <div class="expert-card">
            <div class="expert-header">
                {avatar_html}
                <div class="expert-info">
                    <div class="expert-name">{safe_username}</div>
                    <div class="expert-cluster">{safe_cluster_label}</div>
                </div>
            </div>
            {f'<div class="expert-bullets"><h4>Areas of Expertise</h4>{bullets_html}</div>' if bullets_html else ''}
            {f'<div class="expert-message"><h4>Representative Message</h4><div class="expert-message-text">&ldquo;{safe_message_content}&rdquo;</div></div>' if message_content else ''}
        </div>
        """
    
    html_content += '</div></div>'
    return html_content

