import express from "express";
import {
  registerFarmer,
  loginFarmer,
  getProfile,
} from "../controllers/authController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

router.post("/register", registerFarmer);
router.post("/login", loginFarmer);
router.get("/me", protect, getProfile);

export default router;
