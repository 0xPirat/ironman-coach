package de.johannesbenedict.ironmancoach

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.viewmodel.compose.viewModel
import de.johannesbenedict.ironmancoach.ui.CoachApp
import de.johannesbenedict.ironmancoach.ui.CoachViewModel
import de.johannesbenedict.ironmancoach.ui.IronmanCoachTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            IronmanCoachTheme {
                val coachViewModel: CoachViewModel = viewModel()
                CoachApp(coachViewModel)
            }
        }
    }
}
