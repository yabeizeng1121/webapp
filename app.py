import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from PIL import Image
import modelbit
import json

im = Image.open("imgs/favicon.ico")
st.set_page_config(
    page_title="Champion Edge", page_icon=im, initial_sidebar_state="collapsed"
)

# Load the data
input_data = pd.read_csv("data/input_data.csv")
champ_career_stats = pd.read_csv(
    "https://media.githubusercontent.com/media/yabeizeng1121/champions_edge/main/data/champ_career_stats.csv"
)
champion_list = champ_career_stats["champion"].tolist()


# Helper function to update input data based on user selections
def update_input_data(input_data, selections):
    # Reset all player and opponent picks to 0
    player_columns = [f"PlayerPick_{champ}" for champ in champion_list]
    opponent_columns = [f"OppPick_{champ}" for champ in champion_list]
    input_data.loc[:, player_columns + opponent_columns] = 0

    # Update the dataframe to set selected champions to 1
    for champ in selections["player"]:
        column_name = f"PlayerPick_{champ}"
        input_data.loc[:, column_name] = 1

    for champ in selections["opponent"]:
        column_name = f"OppPick_{champ}"
        input_data.loc[:, column_name] = 1

    return input_data


# Helper function to update champion stats based on user selections
def update_champion_stats(input_data, champ_career_stats, champion1):
    # Extract the row corresponding to champion1's career stats
    champ_stats = champ_career_stats.loc[
        champ_career_stats["champion"] == champion1
    ].drop("champion", axis=1)
    # Update the input data with the selected champion's stats
    input_data.loc[:, champ_stats.columns] = champ_stats.values[0]
    return input_data


# Helper function to get a list of champions that have not been selected
def get_available_champions(picked_champs, all_champs):
    return list(set(all_champs) - set(picked_champs))


# Helper function to update input data with picks
def update_input_data_with_picks(input_data, team_picks, opponent_picks):
    for pick in team_picks:
        input_data[f"PlayerPick_{pick}"] = 1
    for pick in opponent_picks:
        input_data[f"OppPick_{pick}"] = 1
    return input_data


def predict(input_data):
    response = modelbit.get_inference(
        region="us-east-1",
        workspace="yabeizeng",
        deployment="predict_win_rate",
        data=json.dumps(
            input_data.to_dict(orient="records")
        ),  # Serialize DataFrame to JSON
    )
    return response["data"]


# Helper function to prepare the input data with current picks and the new champion
def make_prediction_for_champion(champion, input_data, team_picks, opponent_picks):
    input_data_updated = update_input_data_with_picks(
        input_data.copy(), team_picks, opponent_picks
    )
    # Set the new champion as the team's pick
    input_data_updated[f"PlayerPick_{champion}"] = 1
    input_data_updated = update_champion_stats(
        input_data_updated, champ_career_stats, champion
    )
    return predict(input_data_updated)


# Helper function to recommend champions
def recommend_champions(input_data, all_champions, team_picks, opponent_picks):
    available_champions = get_available_champions(
        team_picks + opponent_picks, all_champions
    )
    champion_recommendations = []

    # Predict win rate for all available champions
    for champion in available_champions:
        win_rate = make_prediction_for_champion(
            champion, input_data, team_picks, opponent_picks
        )
        champion_recommendations.append((champion, win_rate))

    # Sort champions based on the predicted win rate and take the top three
    champion_recommendations.sort(key=lambda x: x[1], reverse=True)
    return champion_recommendations[:5]


tab1, tab2, tab3 = st.tabs(["Intro", "Winning Prediction", "Champion Recommendation"])

st.markdown(
    """
    <style>
    .custom-text {
        color: #9c9d9f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
with tab1:
    st.subheader("| Intro")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.image("imgs/lol_intro.png")
        st.caption("The Most Overpowered League of Legends Champions on Release")

    with col2:
        intro_text = """
        Welcome to ChampionEdge, League enthusiasts! Imagine stumbling upon a secret mushroom patch in Summoner’s Rift - that’s us, offering a clever way to pick champions. With our concoction of advanced machine learning, we’re here to predict victories and suggest champions tailored to your playstyle, giving you the edge before the battle even begins. 
        Strap in as we embark on a quest to outsmart the opposition, armed with data-driven insights and strategic recommendations. Whether you're climbing solo queue or teaming up for flex, ChampionEdge is your guide to making informed choices that turn the tide of battle in your favor. 
        Ready for a smarter way to play, combining strategy with a hint of Teemo’s cunning? ChampionEdge is here to lead the charge. Let’s dive into the Rift, champions - victory awaits with every smart pick!
        """
        st.markdown(f'<p class="custom-text">{intro_text}</p >', unsafe_allow_html=True)
        audio_file = open("audio/song.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mpeg")

    st.subheader("| Developer")
    st.markdown(
        '<p class="custom-text">Thanks to our amazing Pangolin team </p >',
        unsafe_allow_html=True,
    )

    st.subheader("| Github")
    st.markdown(
        '<p class="custom-text">This site is based on <a href=" " style="color: #9c9d9f;">GitHub</a >. Edit your levels with <a href="https://dungeon-editor.streamlit.app/" style="color: #9c9d9f;">The Dungeon editor</a >.</p >',
        unsafe_allow_html=True,
    )


with tab2:
    st.subheader("| Winning Predictor")
    # Champion selection dropdown
    champion1 = st.selectbox(
        "Choose your champion 1:", champion_list, index=champion_list.index("Wukong")
    )
    champion2 = st.selectbox(
        "Choose your champion 2:", champion_list, index=champion_list.index("Darius")
    )
    champion3 = st.selectbox(
        "Choose your champion 3:", champion_list, index=champion_list.index("Rengar")
    )
    champion4 = st.selectbox(
        "Choose your champion 4:",
        champion_list,
        index=champion_list.index("Twisted Fate"),
    )
    champion5 = st.selectbox(
        "Choose your champion 5:", champion_list, index=champion_list.index("Kai'Sa")
    )
    champion_op_1 = st.selectbox(
        "Choose your opponent's champion 1:",
        champion_list,
        index=champion_list.index("Garen"),
    )
    champion_op_2 = st.selectbox(
        "Choose your opponent's champion 2:",
        champion_list,
        index=champion_list.index("Master Yi"),
    )
    champion_op_3 = st.selectbox(
        "Choose your opponent's champion 3:",
        champion_list,
        index=champion_list.index("Lux"),
    )
    champion_op_4 = st.selectbox(
        "Choose your opponent's champion 4:",
        champion_list,
        index=champion_list.index("Ashe"),
    )
    champion_op_5 = st.selectbox(
        "Choose your opponent's champion 5:",
        champion_list,
        index=champion_list.index("Lulu"),
    )
    # Predict button
    if st.button("Predict Winning Rate"):
        # Get user's champion selections
        selections = {
            "player": [champion1, champion2, champion3, champion4, champion5],
            "opponent": [
                champion_op_1,
                champion_op_2,
                champion_op_3,
                champion_op_4,
                champion_op_5,
            ],
        }

        # Update the input data
        input_data = update_input_data(input_data, selections)
        input_data = update_champion_stats(input_data, champ_career_stats, champion1)

        # Predict the winning rate
        winning_rate = predict(input_data)
        winning_rate_percent = "{:.2%}".format(winning_rate)

        # Display the predicted winning rate within a chatbox style
        col1, col2 = st.columns([1, 5], gap="small")

        with col1:
            st.image("imgs/teemo.png", width=50)  # Adjust width as needed

        with col2:
            st.markdown(
                f"""
                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; color: #333333;">
                Your winning rate is {winning_rate_percent}
                </div>
                """,
                unsafe_allow_html=True,
            )


with tab3:
    st.subheader("| Champion Recommendation")
    # Champion selection dropdown
    team_champ2 = st.selectbox(
        "Choose your team champion 1:",
        champion_list,
        index=champion_list.index("Darius"),
    )
    team_champ3 = st.selectbox(
        "Choose your team champion 2:",
        champion_list,
        index=champion_list.index("Rengar"),
    )
    team_champ4 = st.selectbox(
        "Choose your team champion 3:",
        champion_list,
        index=champion_list.index("Twisted Fate"),
    )
    team_champ5 = st.selectbox(
        "Choose your team champion 4:",
        champion_list,
        index=champion_list.index("Kai'Sa"),
    )
    oppo_champ1 = st.selectbox(
        "Choose opponent's champion 1:",
        champion_list,
        index=champion_list.index("Garen"),
    )
    oppo_champ2 = st.selectbox(
        "Choose opponent's champion 2:",
        champion_list,
        index=champion_list.index("Master Yi"),
    )
    oppo_champ3 = st.selectbox(
        "Choose opponent's champion 3:", champion_list, index=champion_list.index("Lux")
    )
    oppo_champ4 = st.selectbox(
        "Choose opponent's champion 4:",
        champion_list,
        index=champion_list.index("Ashe"),
    )
    oppo_champ5 = st.selectbox(
        "Choose opponent's champion 5:",
        champion_list,
        index=champion_list.index("Lulu"),
    )
    team_picks = [team_champ2, team_champ3, team_champ4, team_champ5]
    opponent_picks = [oppo_champ1, oppo_champ2, oppo_champ3, oppo_champ4, oppo_champ5]

    # Predict button
    if st.button("Find your best champion"):
        # Use the functions to get the top three recommended champions
        top_three_champions = recommend_champions(
            input_data, champion_list, team_picks, opponent_picks
        )

        # Display the predicted winning rate within a chatbox style
        col1, col2 = st.columns([1, 5], gap="small")

        with col1:
            st.image("imgs/teemo.png", width=50)  # Adjust width as needed

        # Iterate over the top three champions and display them
        for idx, (champ, rate) in enumerate(top_three_champions, start=1):
            win_rate_percent = "{:.2%}".format(
                rate
            )  # Format as percentage with two decimals

            # Render the champion and its win rate in Streamlit's markdown
            with col2:
                st.markdown(
                    f"""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; color: #333333;">
                    <b>Option {idx}:</b> Pick <b>{champ}</b> for an estimated win rate of <b>{win_rate_percent}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
